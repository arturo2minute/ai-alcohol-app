from typing import Optional


# Supported verification fields and their UI labels.
FIELD_DEFINITIONS = [
    {"key": "brandName", "label": "Brand Name"},
    {"key": "classType", "label": "Class/Type"},
    {"key": "alcoholContent", "label": "Alcohol Content"},
    {"key": "netContents", "label": "Net Contents"},
    {"key": "governmentWarning", "label": "Government Warning"},
]

WARNING_PLACEHOLDER_TEXT = "Placeholder warning text requires OCR validation"


# Builds the placeholder verification payload returned by POST /verify.
def build_placeholder_verification(
    *,
    original_name: str,
    mime_type: Optional[str],
    size_bytes: int,
    brand_name: Optional[str],
    class_type: Optional[str],
    alcohol_content: Optional[str],
    net_contents: Optional[str],
    government_warning: Optional[str],
) -> dict:
    
    # Find expected and detected fields
    expected_fields = {
        "brandName": normalize_value(brand_name),
        "classType": normalize_value(class_type),
        "alcoholContent": normalize_value(alcohol_content),
        "netContents": normalize_value(net_contents),
        "governmentWarning": normalize_value(government_warning),
    }
    detected_fields = build_placeholder_detected_fields(expected_fields)

    # Get Results
    results = build_placeholder_results(expected_fields, detected_fields)
    summary = summarize_results(results)

    return {
        "file": {
            "originalName": original_name,
            "mimeType": mime_type,
            "sizeBytes": size_bytes,
        },
        "expectedFields": expected_fields,
        "results": results,
        "summary": summary,
        "placeholder": True,
        "note": "Placeholder verification only. OCR and real extraction are not implemented yet.",
    }


# Builds placeholder detected values until OCR is available.
def build_placeholder_detected_fields(expected_fields: dict[str, str]) -> dict[str, str]:
    detected_fields = {}

    for field_definition in FIELD_DEFINITIONS:
        field_key = field_definition["key"]
        expected_value = expected_fields[field_key]

        if field_key == "governmentWarning" and expected_value:
            has_uppercase_prefix = "GOVERNMENT WARNING:" in expected_value
            detected_fields[field_key] = (
                expected_value if has_uppercase_prefix else WARNING_PLACEHOLDER_TEXT
            )
            continue

        detected_fields[field_key] = expected_value

    return detected_fields


# Builds the per-field verification rows from expected and detected values.
def build_placeholder_results(
    expected_fields: dict[str, str], detected_fields: dict[str, str]
) -> list[dict]:
    results = []

    for field_definition in FIELD_DEFINITIONS:
        field_key = field_definition["key"]
        expected_value = expected_fields[field_key]
        detected_value = detected_fields[field_key]
        result = build_placeholder_result(
            field_definition,
            expected_value,
            detected_value,
        )
        results.append(result)

    return results


# Builds one row in the results table using temporary placeholder rules.
def build_placeholder_result(
    field_definition: dict[str, str], expected_value: str, detected_value: str
) -> dict:
    if not expected_value:
        return {
            "field": field_definition["label"],
            "expectedValue": "",
            "detectedValue": "",
            "status": "Needs Review",
            "notes": "No expected value provided.",
        }

    if field_definition["key"] == "governmentWarning":
        if detected_value != expected_value:
            status = "Mismatch"
            notes = (
                "Expected warning should include the uppercase 'GOVERNMENT WARNING:' prefix."
            )
        else:
            status = "Match"
            notes = "Placeholder match until OCR is implemented."

        return {
            "field": field_definition["label"],
            "expectedValue": expected_value,
            "detectedValue": detected_value,
            "status": status,
            "notes": notes,
        }

    return {
        "field": field_definition["label"],
        "expectedValue": expected_value,
        "detectedValue": detected_value,
        "status": "Match",
        "notes": "Placeholder match until OCR is implemented.",
    }


# Summarizes the results for the UI header.
def summarize_results(results: list[dict]) -> dict[str, int]:
    summary = {
        "total": 0,
        "Match": 0,
        "Mismatch": 0,
        "Needs Review": 0,
    }

    for result in results:
        summary["total"] += 1
        summary[result["status"]] += 1

    return summary


# Trims text input so blank and whitespace-only values are handled consistently.
def normalize_value(value: Optional[str]) -> str:
    return value.strip() if isinstance(value, str) else ""
