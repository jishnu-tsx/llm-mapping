import os

from route_llm_config import LLMRouter

import google.generativeai as genai
from fastapi import APIRouter, HTTPException

from balance_sheet.models import (
    BsCompleteMappingWithNotesRequest,
    BSSectionMappingRequestModel,
)
from utils import pdf_to_images, generate_json_from_llm_output, convert_to_md_using_llm
from dotenv import load_dotenv
from genai_router.router import GenAIRouter


gen_ai_router = GenAIRouter(provider="ollama", model="gpt-oss:latest")
# gen_ai_router = GenAIRouter(provider="gemini", model="gemini-1.5-flash")


load_dotenv()

router = APIRouter()
llm_router = LLMRouter()
# === Configuration ===
API_KEY = os.getenv("GOOGLE_API_KEY")
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

genai.configure(api_key=API_KEY)


# ========== Routes ==========


@router.post("/bs-mapping")
def bs_mapping(request_data: BsCompleteMappingWithNotesRequest):
    """
    Extract balance sheet data from specified page range,
    run Gemini mapping, and update balance sheet JSON.
    """
    try:
        bs_start_page, bs_end_page = (
            request_data.bs_start_page,
            request_data.bs_end_page,
        )
        company_id = request_data.company_id
        afs_path = os.path.join(BASE_DIR, "afs", f"{company_id}_afs.pdf")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {e}")

    # Convert BS PDF to images
    image_paths = pdf_to_images(afs_path, bs_start_page, bs_end_page)

    # Load prompt
    try:
        prompt_path = os.path.join(BASE_DIR, "prompts", "balance_sheet", "v1", "bs.md")
        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt = f.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading prompt: {e}")

    # Upload images
    user_input = prompt + "\n\nAttached images:\n" + "\n".join(image_paths)

    # Call Gemini
    try:
        response_text = gen_ai_router.route(user_input, image_paths)
        print("LLM Response:", response_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calling routed LLM: {e}")

    # Update BS JSON
    bs_json_path = os.path.join(BASE_DIR, "json", "balance_sheet", "bs.json")
    bs_formatted_json_path = os.path.join(
        BASE_DIR, "json", "balance_sheet", "bs_formatted.json"
    )
    path_to_store_op = os.path.join(BASE_DIR, "results", "balance_sheet", "bs.json")
    generate_json_from_llm_output(
        bs_json_path, response_text, path_to_store_op, bs_formatted_json_path
    )

    return {"status": "success", "message": "Mapping done, check logs for output"}


@router.post("/bs-mapping-w-notes")
def bs_mapping_w_notes(request_data: BsCompleteMappingWithNotesRequest):
    """
    Perform balance sheet + notes mapping with Gemini.
    """
    try:
        bs_start_page, bs_end_page = (
            request_data.bs_start_page,
            request_data.bs_end_page,
        )
        notes_start_page, notes_end_page = (
            request_data.notes_start_page,
            request_data.notes_end_page,
        )
        afs_path = os.path.join(BASE_DIR, "afs", f"{request_data.company_id}_afs.pdf")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {e}")

    # Convert BS & Notes PDF pages to images
    bs_image_paths = pdf_to_images(afs_path, bs_start_page, bs_end_page)
    notes_image_paths = pdf_to_images(afs_path, notes_start_page, notes_end_page)

    # Load prompt
    try:
        prompt_path = os.path.join(
            BASE_DIR, "prompts", "balance_sheet_with_notes", "v1", "bs_with_notes.md"
        )
        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt = f.read()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error reading BS+Notes prompt: {e}"
        )

    try:
        response_text = gen_ai_router.route(
            prompt, (bs_image_paths + notes_image_paths)
        )
        print("LLM Response:", response_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calling routed LLM: {e}")
    bs_json_path = os.path.join(BASE_DIR, "json", "balance_sheet", "bs.json")
    bs_formatted_json_path = os.path.join(
        BASE_DIR, "json", "balance_sheet", "bs_formatted.json"
    )
    path_to_store_op = os.path.join(BASE_DIR, "results", "bs_w_notes.json")
    generate_json_from_llm_output(
        bs_json_path, response_text, path_to_store_op, bs_formatted_json_path
    )

    return {"status": "success", "message": "Balance Sheet + Notes mapping completed."}


@router.post("/bs-section-mapping")
def section_mapping(request: BSSectionMappingRequestModel):
    """
    Perform section-wise Balance Sheet mapping.
    Extract section markdown via Ollama Gemma, then refine with Gemini.
    """
    #! For local model uncomment this
    # _gen_ai_router = GenAIRouter(provider="local", model="deepseek-r1:8b")
    afs_path = os.path.join(BASE_DIR, "afs", f"{request.company_id}_afs.pdf")

    # Convert note pages + BS pages to images
    notes_image_paths = []
    for page_no in request.note_page_nos:
        page_no = int(page_no)
        notes_image_paths.extend(pdf_to_images(afs_path, page_no, page_no))

    bs_image_paths = pdf_to_images(
        afs_path, int(request.bs_start_page), int(request.bs_end_page)
    )

    # Encode BS images to base64
    # encoded_images = []
    # for img_path in bs_image_paths:
    #     with open(img_path, "rb") as f:
    #         encoded_images.append(base64.b64encode(f.read()).decode("utf-8"))

    # Call Ollama Gemma for section markdown
    # Todo: Implement this using db
    md_convert_prompt_path = os.path.join(
        BASE_DIR, "prompts", "md_convert", "v1", "md_convert.md"
    )

    with open(md_convert_prompt_path, "r", encoding="utf-8") as f:
        md_convert_prompt = f.read()
    section_name = request.section.name.replace("_", " ")
    md_convert_prompt = md_convert_prompt.replace("{section_name}", section_name)

    md_convert_prompt = md_convert_prompt.replace("{FY1}", request.fy1)
    md_convert_prompt = md_convert_prompt.replace("{FY2}", request.fy2)
    section_markdown = convert_to_md_using_llm(md_convert_prompt, bs_image_paths)

    #! Converting notes to md : currently done in ollama.py
    # with open(os.path.join(md_convert_prompt_path, "notes_image_convert.md"), "r") as f:
    #     notes_convert_prompt = f.read()
    # notes_convert_prompt = notes_convert_prompt.replace("{FY1}", fy_1)
    # notes_convert_prompt = notes_convert_prompt.replace("{FY2}", fy_2)
    # notes_md = ""
    # for note_image_path in notes_image_paths:
    #     notes_md = convert_to_md_using_llm(notes_convert_prompt, note_image_path)
    #     notes_md = notes_md + notes_md
    # Load section-specific prompt
    try:
        prompt_path = os.path.join(
            BASE_DIR,
            "prompts",
            "section_wise",
            "v1",
            f"{request.section.name.lower()}.md",
        )
        with open(prompt_path, "r", encoding="utf-8") as f:
            detailed_prompt = f.read()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error reading section-specific prompt: {e}"
        )

    user_input = (
        detailed_prompt + "\n\nbalance_sheet.md:\n" + "\n".join(section_markdown)
    )

    try:
        response_text = gen_ai_router.route(user_input, notes_image_paths)
        print("LLM Response:", response_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calling routed LLM: {e}")
    bs_formatted_json_path = os.path.join(
        BASE_DIR, "json", "balance_sheet", "bs_formatted.json"
    )
    result_path = (
        os.path.join(BASE_DIR, "results", "bs_w_notes.json")
        if os.path.exists(os.path.join(BASE_DIR, "results", "bs_w_notes.json"))
        else os.path.join(BASE_DIR, "results", "bs.json")
    )

    generate_json_from_llm_output(
        result_path,
        response_text,
        result_path,
        bs_formatted_json_path,
        update_mode=True,
    )

    return {
        "status": "success",
        "section": request.section.name,
    }
