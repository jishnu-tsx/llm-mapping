import base64
import copy
import os
from typing import List
from fastapi import HTTPException
import fitz  # PyMuPDF
import re
import json
from difflib import get_close_matches
import google.generativeai as genai
import requests

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def pdf_to_images(pdf_path, start_page, end_page):
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
    """Convert string numbers to float if possible."""
    if isinstance(value, str):
        value = value.strip().replace(",", "")
        try:
            return float(value)
        except ValueError:
            return value
    return value


def parse_plaintext_output(plain_text: str):
    """
    Parse entries from plain text Gemini/Gemma-like output.
    Each entry has keys: name, value_of_financial_year_1, value_of_financial_year_2, source.
    """
    pattern = re.compile(
        r'\{\s*"name"\s*:\s*"(?P<name>.*?)"\s*,\s*'
        r'"value_of_financial_year_1"\s*:\s*(?P<val1>-?[\d\.]+)\s*,\s*'
        r'"value_of_financial_year_2"\s*:\s*(?P<val2>-?[\d\.]+)\s*,\s*'
        r'"source"\s*:\s*"(?P<source>.*?)"\s*\}',
        re.DOTALL,
    )

    results = []
    for match in pattern.finditer(plain_text):
        name = match.group("name").strip()
        val1 = clean_numeric_value(match.group("val1"))
        val2 = clean_numeric_value(match.group("val2"))
        source = match.group("source").strip()

        results.append(
            {
                "name": name,
                "value_of_financial_year_1": val1,
                "value_of_financial_year_2": val2,
                "source": source,
            }
        )
    return results


def update_balance_sheet(
    json_path: str,
    plain_text: str,
    output_path: str,
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
        balance_sheet = json.load(f)

    # Reset ocr_value if not in update mode
    if not update_mode:
        for item in balance_sheet:
            item["ocr_value"] = None

    # Apply updates
    for entry in entries:
        variable = entry["name"].lower().strip()
        val1 = entry["value_of_financial_year_1"]
        val2 = entry["value_of_financial_year_2"]
        source = entry["source"]

        matched = False
        for item in balance_sheet:
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
        json.dump(balance_sheet, f, indent=2, ensure_ascii=False)

    print(f"[INFO] Updated balance sheet saved at {output_path}")

    bs_og_format_path = os.path.join(BASE_DIR, "json", "balance_sheet.json")
    # with open(bs_og_format_path, "w") as f:
    #     bs_og_format = f.read()
    res = process_and_save(
        bs_og_format_path, balance_sheet, os.path.dirname(output_path)
    )
    print(f"Successfully converted and saved at {res}")
    return balance_sheet


def map_ocr_to_balance_sheet(balance_sheet, ocr_items):
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
    updated = map_ocr_to_balance_sheet(balance_sheet, ocr_items)

    # Ensure folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Save to file
    output_path = os.path.join(output_folder, output_filename)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(updated, f, indent=2, ensure_ascii=False)

    return output_path


OLLAMA_API_URL = os.getenv("OLLAMA_URL")


def convert_to_md(prompt: str, image_path: List[str]) -> str:
    """
    Send a prompt + image to Ollama Gemma model and return the markdown response.

    Args:
        prompt (str): The text prompt.
        image_path (str): Path to the image file.

    Returns:
        str: Markdown response content.
    """
    try:
        # Encode image to base64
        encoded_images = []
        for image in image_path:
            with open(image, "rb") as f:
                encoded_images.append(base64.b64encode(f.read()).decode("utf-8"))

        payload = {
            "model": "gemma3:4b",
            "stream": False,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                    "images": encoded_images,  # list of one image
                }
            ],
        }

        response = requests.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status()

        gemma_response = response.json()
        section_markdown = gemma_response.get("message", {}).get("content", "")

        print(f"Response from geamma {section_markdown}")
        return section_markdown
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error calling Ollama Gemma API: {e}"
        )
