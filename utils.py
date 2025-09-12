import base64
import copy
import os
import json5
from typing import List
from fastapi import HTTPException
import fitz  # PyMuPDF
import re
import json
from difflib import get_close_matches
import google.generativeai as genai
import requests
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered

# Todo: Implement Logging

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def convert_image_b64(image_path: str) -> str:
    """
    Convert a image file into eqvalent base64 format for llms
    """
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def pdf_to_images(pdf_path, start_page, end_page) -> list:
    """
    Convert the pages of the given pdf into images and stores it

    Arguments:
        pdf_path (str): The file path to the input PDF document.
        start_page (int): The starting page number for conversion (1-indexed, inclusive).
        end_page (int): The ending page number for conversion (1-indexed, inclusive).

    returns: A lsit containg the paths of the converted images
    """

    # Todo: Convert all data storing operation to be done in DB
    image_paths = []
    parent_dir = os.path.dirname(pdf_path)
    images_dir = os.path.join(parent_dir, "images")
    os.makedirs(images_dir, exist_ok=True)

    doc = fitz.open(pdf_path)

    for i in range(start_page - 1, end_page):  # 0-based
        image_path = os.path.join(images_dir, f"{i + 1}.png")

        if os.path.exists(image_path):
            # If image already exists, reuse it
            print(f"exists: {image_path}")
            image_paths.append(image_path)
            continue

        # Otherwise generate a new image
        page = doc[i]
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # zoom factor
        pix.save(image_path)
        print(f"saved: {image_path}")
        image_paths.append(image_path)

    return image_paths


def clean_numeric_value(value):
    """Convert string numbers to float if possible, handle null/N/A."""
    if value in [None, "null", "Null", "NULL", "N/A", "-", ""]:
        return None
    if isinstance(value, str):
        value = value.strip().replace(",", "")
        try:
            return float(value)
        except ValueError:
            return value
    return value


def extract_json_block(plain_text: str):
    """
    Extract the first valid JSON-like array/object from messy LLM output.
    Handles ```json fences, or bare { ... } / [ ... ] blocks.
    """
    # Case 1: inside fenced ```json ... ```
    fenced = re.findall(r"```json(.*?)```", plain_text, flags=re.DOTALL | re.IGNORECASE)
    if fenced:
        return fenced[0].strip()

    # Case 2: first array/object in the text
    match = re.search(r"(\{.*\}|\[.*\])", plain_text, flags=re.DOTALL)
    if match:
        return match.group(1).strip()

    return None


def normalize_json_like(text: str) -> str:
    """
    Normalize Python/LLM-style JSON into strict JSON:
    - Replace None → null
    - Replace single quotes → double quotes
    """
    text = re.sub(r"\bNone\b", "null", text)
    text = text.replace("'", '"')
    return text


def safe_json_loads(s: str) -> dict:
    """
    Checks if a string can be parsed into json if possible loads it
    removes markdown fences , cleans artifacts in data caused by llms

    uses json5 for much more forgiving parsing in case first one fails
    """
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        # Try to strip markdown fences
        if s.strip().startswith("```"):
            s = s.strip().strip("`")
            if s.startswith("json"):
                s = s[4:].strip()
        # Optionally: use a library like `json5` or `demjson3` for loose parsing
        s = re.sub(r"\(([-+]?\d+(\.\d+)?)\)", r"-\1", s)

        return json5.loads(s)


def parse_plaintext_output(plain_text: str) -> list:
    """
    Parse entries from messy Gemini/Gemma-like output.
    Handles extra tables/thinking text before/after JSON and Python-style None.
    """
    json_block = extract_json_block(plain_text)
    if not json_block:
        raise ValueError("No JSON block found in the plain text output")

    # normalize before parsing
    json_block = normalize_json_like(json_block)

    try:
        data = safe_json_loads(json_block)
    except json.JSONDecodeError as e:
        raise ValueError(f"Could not parse JSON block: {e}")

    # Normalize into list
    if isinstance(data, dict):
        data = [data]

    results = []
    for entry in data:
        source_value = entry.get("source")

        # * Added cause sometimes llms messes the text inside source field specifically
        if isinstance(source_value, list):
            # join into a single string, or take the first element
            source_value = " ".join(map(str, source_value))
        elif source_value is None:
            source_value = ""
        results.append(
            {
                "name": entry.get("name", "").strip(),
                "value_of_financial_year_1": clean_numeric_value(
                    entry.get("value_of_financial_year_1")
                ),
                "value_of_financial_year_2": clean_numeric_value(
                    entry.get("value_of_financial_year_2")
                ),
                "source": str(source_value).strip(),
            }
        )

    return results


# Todo: Convert all file operation to DB once in server
def generate_json_from_llm_output(
    json_path: str,
    plain_text: str,
    output_path: str,
    formatted_json_path: str,
    threshold: float = 0.85,
    update_mode: bool = False,
):
    """
    Update balance sheet JSON with OCR values from plain text output.

    Args:
        json_path (str): Path to the base balance sheet JSON file.
        plain_text (str): Gemini/Gemma plain text output to parse.
        output_path (str): Path to save the updated balance sheet JSON.
        threshold (float): Similarity threshold for fuzzy matching.
        formatted_json_path: (str): The path of the json file for the final output
        update_mode (bool):
            - True → update only existing ocr_value fields if present.
            - False → reset and freshly map everything.
    """
    # Save raw Gemini/Gemma output for debugging
    gemini_op_path = os.path.join(BASE_DIR, "json", "output", "gemini_op.json")
    with open(gemini_op_path, "w", encoding="utf-8") as f:
        f.write(plain_text)

    entries = parse_plaintext_output(plain_text)
    if not entries:
        raise ValueError("No valid entries found in the plain text output")

    # Load existing JSON
    with open(json_path, "r", encoding="utf-8") as f:
        json_file = json.load(f)

    # Reset ocr_value if not in update mode
    if not update_mode:
        for item in json_file:
            item["ocr_value"] = None

    # Apply updates
    for entry in entries:
        variable = entry["name"].lower().strip()
        val1 = entry["value_of_financial_year_1"]
        val2 = entry["value_of_financial_year_2"]
        source = entry["source"]

        matched = False
        for item in json_file:
            item_name = item.get("name", "").lower().strip()
            if variable == item_name or get_close_matches(
                variable, [item_name], n=1, cutoff=threshold
            ):
                if update_mode and item.get("ocr_value") is not None:
                    print(f"[UPDATE] {entry['name']} → {val1}, {val2}")
                else:
                    print(f"[CREATE] {entry['name']} → {val1}, {val2}")

                # Store as dict instead of single value
                item["ocr_value"] = {
                    "financial_year_1": clean_numeric_value(val1),
                    "financial_year_2": clean_numeric_value(val2),
                    "source": source,
                }

                matched = True
                break

        if not matched:
            print(f"[WARN] No match found for: {entry['name']}")

    # Save output
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(json_file, f, indent=2, ensure_ascii=False)

    print(f"[INFO] Updated balance sheet saved at {output_path}")

    output_file_name = os.path.basename(output_path)
    res = process_and_save(
        formatted_json_path, json_file, os.path.dirname(output_path), output_file_name
    )
    print(f"Successfully converted and saved at {res}")
    return json_file


def map_llm_to_formatted_json(balance_sheet, ocr_items):
    """
    Maps OCR extracted values into the hierarchical balance sheet JSON.

    - balance_sheet: dict representing the uploaded balance_sheet.json
    - ocr_items: list of dicts with keys ["id", "name", "ocr_value"]

    Updates 'ocr_value' field of matching nodes if is_header is True,
    otherwise puts the mapped values into 'value'.
    Puts source string into 'remarks' inside ocr_value.
    """

    def update_node(node, ocr_lookup):
        if not isinstance(node, dict):
            return

        node_id = node.get("id")
        if node_id in ocr_lookup:
            ocr_entry = ocr_lookup[node_id].get("ocr_value")
            if ocr_entry is not None:
                ocr_entry = copy.deepcopy(ocr_entry)
                # Move `source` into remarks
                source = ocr_entry.pop("source", None)
                if source:
                    ocr_entry["remarks"] = source

                if node.get("is_header", False):
                    # For headers → keep whole dict in ocr_value
                    node["ocr_value"] = {
                        "financial_year_1": ocr_entry.get("financial_year_1"),
                        "financial_year_2": ocr_entry.get("financial_year_2"),
                    }
                    if "remarks" in ocr_entry:
                        node["remarks"] = ocr_entry["remarks"]

                else:
                    # For leaf nodes → only numeric values go into value
                    node["value"] = {
                        "financial_year_1": ocr_entry.get("financial_year_1"),
                        "financial_year_2": ocr_entry.get("financial_year_2"),
                    }
                    # Keep remarks separately if present
                    if "remarks" in ocr_entry:
                        node["remarks"] = ocr_entry["remarks"]

        # Recurse into children
        children = node.get("children")
        if isinstance(children, dict):
            for child_node in children.values():
                update_node(child_node, ocr_lookup)

    # Build lookup by id
    ocr_lookup = {item["id"]: item for item in ocr_items}

    # Iterate over all root-level items
    for root_item in balance_sheet.get("items", []):
        update_node(root_item, ocr_lookup)

    return balance_sheet


def process_and_save(
    balance_sheet_path,
    ocr_items,
    output_folder,
    output_filename="updated_balance_sheet.json",
):
    """
    Loads balance sheet JSON, maps OCR values, and saves the updated JSON in the given folder.

    - balance_sheet_path: path to the uploaded balance_sheet.json
    - ocr_items: OCR extracted items
    - output_folder: folder where updated JSON should be saved
    - output_filename: name of output file (default 'updated_balance_sheet.json')
    """
    # Load balance sheet
    with open(balance_sheet_path, "r", encoding="utf-8") as f:
        balance_sheet = json.load(f)

    # Update with OCR values
    updated = map_llm_to_formatted_json(balance_sheet, ocr_items)

    # Ensure folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Save to file
    output_path = os.path.join(output_folder, f"formatted_{output_filename}")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(updated, f, indent=2, ensure_ascii=False)

    return output_path


OLLAMA_API_URL = os.getenv("OLLAMA_URL")


#! Might need to change according to ollama version
def convert_to_md_using_llm(prompt: str, image_path: List[str]) -> str:
    """
    Send a prompt + image to Ollama Gemma model and return the markdown response.

    Args:
        prompt (str): The text prompt.
        image_path (str): Paths to the image files.

    Returns:
        str: Markdown response content.
    """
    section_markdown = ""
    try:
        for image in image_path:
            # Encode image to base64
            encoded_image = convert_image_b64(image)

            payload = {
                "model": "gemma3:4b",
                "stream": False,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt,
                        "images": encoded_image,  # list of one image
                    }
                ],
            }

            response = requests.post(OLLAMA_API_URL, json=payload)
            response.raise_for_status()

            gemma_response = response.json()
            section_markdown += "\n" + gemma_response.get("message", {}).get(
                "content", ""
            )

            print(f"Response from geamma {section_markdown}")
        return section_markdown
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error calling Ollama Gemma API: {e}"
        )


def convert_to_md_using_python(image_path: str):
    """
    Convert an image into its equalent markdown preserving table format using marker-pdf package
    Returns the converted markdown as a string
    """

    converter = PdfConverter(artifact_dict=create_model_dict())
    rendered = converter(image_path)
    text, _, _ = text_from_rendered(rendered)

    # * To save the generated markdown use the save_output fn , imported from output
    return text
