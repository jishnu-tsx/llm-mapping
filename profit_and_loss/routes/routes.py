import os
from fastapi import APIRouter, HTTPException
from genai_router.router import GenAIRouter
from profit_and_loss.models import (
    PLCompleteMappingWithNotesRequest,
    PLSectionMappingRequestModel,
)
from utils import convert_to_md_using_llm, pdf_to_images, generate_json_from_llm_output

router = APIRouter()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
genai_router = GenAIRouter(provider="ollama", model="gpt-oss:latest")
# genai_router = GenAIRouter(provider="gemini", model="gemini-1.5-flash")


@router.post("/pl-mapping")
def profit_and_loss_mapping(request_data: PLCompleteMappingWithNotesRequest):
    try:
        try:
            pl_start_page, pl_end_page = (
                request_data.pl_start_page,
                request_data.pl_end_page,
            )

            afs_path = os.path.join(
                BASE_DIR, "afs", f"{request_data.company_id}_afs.pdf"
            )
        except Exception as e:
            print(f"error {e}")
            raise HTTPException(status_code=400, detail="invalid input")

        image_paths = pdf_to_images(afs_path, pl_start_page, pl_end_page)

        try:
            prompt_path = os.path.join(
                BASE_DIR, "prompts", "profit_and_loss", "v1", "pl.md"
            )
            print(prompt_path)
            with open(prompt_path, "r", encoding="utf-8") as f:
                prompt = f.read()
        except Exception as e:
            print(f"error: {e}")
            raise HTTPException(status_code=500, detail="Error reading prompt")

        user_input = prompt + "\n\n Attached images:\n" + "\n".join(image_paths)

        try:
            response_text = genai_router.route(user_input, image_paths)
            print("LLM Response:", response_text)
        except Exception as e:
            print(f"error : {e}")
            raise HTTPException(status_code=500, detail="Error calling LLM")

        pl_json_path = os.path.join(BASE_DIR, "json", "profit_and_loss", "pl.json")
        pl_formatted_json_path = os.path.join(
            BASE_DIR, "json", "profit_and_loss", "pl_formatted.json"
        )
        path_to_store_op = os.path.join(
            BASE_DIR, "results", "profit_and_loss", "pl.json"
        )
        os.makedirs(os.path.dirname(path_to_store_op), exist_ok=True)
        print("✅")
        generate_json_from_llm_output(
            pl_json_path,
            response_text,
            path_to_store_op,
            pl_formatted_json_path,
        )
        return {"status": "success", "message": "Mapping done, check logs for output"}
    except Exception as e:
        print(f"error : {e}")
        raise HTTPException(status_code=500, detail="Mapping Failed")


@router.post("/pl-mapping-w-notes")
def profit_and_loss_mapping_w_notes(request_data: PLCompleteMappingWithNotesRequest):
    try:
        try:
            pl_start_page, pl_end_page = (
                request_data.pl_start_page,
                request_data.pl_end_page,
            )
            notes_start_page, notes_end_page = (
                request_data.notes_start_page,
                request_data.notes_end_page,
            )

            afs_path = os.path.join(
                BASE_DIR, "afs", f"{request_data.company_id}_afs.pdf"
            )
        except Exception as e:
            print(f"error {e}")
            raise HTTPException(status_code=400, detail="invalid input")

        image_paths = pdf_to_images(afs_path, pl_start_page, pl_end_page)
        notes_image_paths = pdf_to_images(afs_path, notes_start_page, notes_end_page)

        try:
            prompt_path = os.path.join(
                BASE_DIR,
                "prompts",
                "profit_and_loss_with_notes",
                "v1",
                "pl_with_notes.md",
            )
            with open(prompt_path, "r", encoding="utf-8") as f:
                prompt = f.read()
        except Exception as e:
            print(f"error: {e}")
            raise HTTPException(status_code=500, detail="Error reading prompt")

        user_input = (
            prompt
            + "\n\n Attached images:\n"
            + "\n".join(image_paths + notes_image_paths)
        )

        try:
            response_text = genai_router.route(
                user_input, image_paths + notes_image_paths
            )
            print("LLM Response:", response_text)
        except Exception as e:
            print(f"error : {e}")
            raise HTTPException(status_code=500, detail="Error calling LLM")

        pl_json_path = os.path.join(BASE_DIR, "json", "profit_and_loss", "pl.json")
        pl_formatted_json_path = os.path.join(
            BASE_DIR, "json", "profit_and_loss", "pl_formatted.json"
        )
        path_to_store_op = os.path.join(
            BASE_DIR, "results", "profit_and_loss", "pl_with_notes.json"
        )
        os.makedirs(os.path.dirname(path_to_store_op), exist_ok=True)

        generate_json_from_llm_output(
            pl_json_path,
            response_text,
            path_to_store_op,
            pl_formatted_json_path,
        )
        return {"status": "success", "message": "Mapping done, check logs for output"}
    except Exception as e:
        print(f"error : {e}")
        raise HTTPException(status_code=500, detail="Mapping Failed")


@router.post("/pl-section-mapping")
def pl_section_mappinf(request_data: PLSectionMappingRequestModel):
    """
    Perform section-wise profit and loss statement mapping
    Extarct section wise markdown via local llm
    Use the llm initialised by genAiRouter to perform the section wise mapping ,
    using only the markdown of the specific entries in the main statement and the notes of those entires given by user

    Returns:
    200: if mapping is correct
    500: if something goes wrong with proper message
    """
    try:
        # Fetching the audited financial statement path
        try:
            # Todo: Implement this using db
            afs_path = os.path.join(
                BASE_DIR, "afs", f"{request_data.company_id}_afs.pdf"
            )
        except Exception as e:
            print(f"Error: {e}")

            raise
        # Dividing the afs into notes pages based on user input and converting them to images and adding their paths to a list
        notes_image_paths = []
        for page_no in request_data.note_page_nos:
            page_no = int(page_no)
            notes_image_paths.extend(pdf_to_images(afs_path, page_no, page_no))
        # Dividing teh afs into pl statemnt and converting it to images
        pl_image_paths = pdf_to_images(
            afs_path, int(request_data.pl_start_page), int(request_data.pl_end_page)
        )
        # Todo: Implement this using db
        md_convert_prompt_path = os.path.join(
            BASE_DIR, "prompts", "md_convert", "v1", "md_convert.md"
        )
        # loading the prompt to extarct the needed section from the pl image as markdown
        with open(md_convert_prompt_path, "r", encoding="utf-8") as f:
            md_convert_prompt = f.read()

        section_name = request_data.section.name.replace("_", "")
        md_convert_prompt = md_convert_prompt.replace("{section_name}", section_name)
        md_convert_prompt = md_convert_prompt.replace("{FY1}", request_data.fy1)
        md_convert_prompt = md_convert_prompt.replace("{FY2}", request_data.fy2)

        # Using local running llm to extract the specific section for mapping from the full pl image(s)
        section_markdown = convert_to_md_using_llm(md_convert_prompt, pl_image_paths)

        # Loading the prompt specific to the section to be mapped
        try:
            # Todo: Implement this using db
            prompt_path = os.path.join(
                BASE_DIR,
                "prompts",
                "pl_section_wise",
                "v1",
                f"{request_data.section.name.lower()}.md",
            )
            with open(prompt_path, "r", encoding="utf-8") as f:
                mapping_prompt = f.read()
        except Exception as e:
            print(f"Error: {e}")
            raise

        # Adding the specific pl section  markdown (generated by gemma) to the mapping prompt
        detailed_prompt = (
            mapping_prompt + "\n\nbalance_sheet.md:\n" + "\n".join(section_markdown)
        )

        # Calling GenAi router to perform the mapping
        try:
            response_text = genai_router.route(detailed_prompt, notes_image_paths)
            print("LLM Reponse: ", response_text)
        except Exception as e:
            print(f"Error: {e}")
            raise

        # The path where the final output format json file is
        pl_formatted_json_path = os.path.join(
            BASE_DIR, "json", "profit_and_loss", "pl_formatted.json"
        )

        # if we did the previous mapping by passing the notes along with the full statement , use that output otherwise use the output generated non-notes mapping
        result_path = (
            os.path.join(BASE_DIR, "results", "profit_and_loss", "pl_w_notes.json")
            if os.path.exists(
                os.path.join(BASE_DIR, "results", "profit_and_loss", "pl_w_notes.json")
            )
            else os.path.join(BASE_DIR, "results", "pl.json")
        )

        # Calling utility function that maps the llm response to the required output json
        generate_json_from_llm_output(
            result_path,
            response_text,
            result_path,
            pl_formatted_json_path,
            update_mode=True,
        )
        return {
            "status": "success",
            "section": request_data.section.name,
        }

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Error doing section mapping")
