import os
import re
import json
from difflib import get_close_matches


def clean_numeric_value(value: str) -> str:
    """Clean numeric value by removing commas and whitespace."""
    if not value:
        return value
    return re.sub(r",", "", value.strip())


def update_node_ocr(
    node: dict,
    variable: str,
    values: list[str],
    path: str = "",
    threshold: float = 0.75,
) -> bool:
    """
    Recursively search for a node with matching 'name' and update its ocr_value.
    """
    node_name = node.get("name", "").strip()
    variable_norm = variable.strip().lower()
    node_name_norm = node_name.lower()

    # Exact match
    if variable_norm == node_name_norm:
        node["ocr_value"] = values
        print(f"[SUCCESS] Exact match at {path + node_name}: {values}")
        return True

    # Fuzzy match
    if get_close_matches(variable_norm, [node_name_norm], n=1, cutoff=threshold):
        node["ocr_value"] = values
        print(f"[SUCCESS] Fuzzy match at {path + node_name}: {values}")
        return True

    # Recurse into children
    if "children" in node and isinstance(node["children"], dict):
        for child in node["children"].values():
            if update_node_ocr(
                child, variable, values, path + node_name + " → ", threshold
            ):
                return True

    return False


def update_balance_sheet(json_path: str, gemini_output: str, threshold: float = 0.75):
    """
    Update balance sheet JSON with values from Gemini output.
    """
    # Load JSON
    with open(json_path, "r", encoding="utf-8") as f:
        balance_sheet = json.load(f)

    for line_num, line in enumerate(gemini_output.splitlines(), 1):
        line = line.strip()

        # Skip empty lines and headers
        if (
            not line
            or line.startswith("| Variable")
            or line.startswith("|---")
            or line.startswith("----")
        ):
            continue

        variable, mapped_value = None, None

        # Markdown table style
        if "|" in line:
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if len(parts) >= 2:
                variable = parts[0]
                mapped_value = parts[1]
        # Colon style
        elif ":" in line:
            variable, mapped_value = line.split(":", 1)
            variable, mapped_value = variable.strip(), mapped_value.strip()

        if not variable or not mapped_value:
            continue

        if mapped_value.upper() in {"(N/A)", "NA", "NOT AVAILABLE", ""}:
            continue

        # Clean value
        cleaned_value = clean_numeric_value(mapped_value)
        values = [
            clean_numeric_value(v.strip())
            for v in re.split(r"[;]", cleaned_value)
            if v.strip()
        ]

        # Traverse all items in JSON
        matched = False
        for item in balance_sheet.get("items", []):
            if update_node_ocr(item, variable, values, path="", threshold=threshold):
                matched = True
                break

        if not matched:
            print(f"[WARN] No match found for: {variable}")

    # Save updated JSON
    json_dir = os.path.dirname(json_path)
    output_dir = os.path.join(json_dir, "output")
    os.makedirs(output_dir, exist_ok=True)
    op_path = os.path.join(output_dir, "output.json")

    with open(op_path, "w", encoding="utf-8") as f:
        json.dump(balance_sheet, f, indent=2, ensure_ascii=False)

    print(f"[INFO] Updated balance sheet saved to: {op_path}")
    return balance_sheet


# Test function to help debug
def test_table_parsing(gemini_output: str):
    """
    Test function to see how the table is being parsed
    """
    print("=== TABLE PARSING TEST ===")
    for line_num, line in enumerate(gemini_output.splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("| Variable") or line.startswith("|---"):
            continue

        if "|" in line:
            parts = [p.strip() for p in line.split("|") if p.strip()]
            print(f"Line {line_num}: {len(parts)} parts -> {parts}")
        else:
            print(f"Line {line_num}: Not a table row -> {line}")
