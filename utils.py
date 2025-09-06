import os
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


# def update_balance_sheet(json_path: str, plain_text: str, threshold: float = 0.85):
#     """Update balance sheet JSON with OCR values from plain text output."""
#     with open("gemini_op.json", "w") as f:
#         f.write(plain_text)
#     entries = parse_plaintext_output(plain_text)
#     if not entries:
#         raise ValueError("No valid entries found in the plain text output")

#     with open(json_path, "r", encoding="utf-8") as f:
#         balance_sheet = json.load(f)

#     for entry in entries:
#         variable = entry["name"].lower().strip()

#         mapped_value = entry["value"]

#         matched = False
#         for item in balance_sheet:
#             item_name = item.get("name", "").lower().strip()
#             if variable == item_name or get_close_matches(
#                 variable, [item_name], n=1, cutoff=threshold
#             ):
#                 item["ocr_value"] = clean_numeric_value(mapped_value)
#                 print(f"[SUCCESS] Mapped {entry['name']} → {mapped_value}")
#                 matched = True
#                 break

#         if not matched:
#             print(f"[WARN] No match found for: {entry['name']}")

#     # Save output
#     out_dir = os.path.join(os.path.dirname(json_path), "output")
#     os.makedirs(out_dir, exist_ok=True)
#     out_path = os.path.join(out_dir, "output.json")

#     with open(out_path, "w", encoding="utf-8") as f:
#         json.dump(balance_sheet, f, indent=2, ensure_ascii=False)

#     print(f"[INFO] Updated balance sheet saved at {out_path}")
#     return balance_sheet


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
    return balance_sheet
