import re
from difflib import SequenceMatcher


# Supported verification fields and their UI labels.
FIELD_DEFINITIONS = [
    {"key": "brandName", "label": "Brand Name"},
    {"key": "classType", "label": "Class/Type"},
    {"key": "alcoholContent", "label": "Alcohol Content"},
    {"key": "netContents", "label": "Net Contents"},
    {"key": "governmentWarning", "label": "Government Warning"},
]

STANDARD_GOVERNMENT_WARNING = (
    "GOVERNMENT WARNING: (1) According to the Surgeon General, women should not "
    "drink alcoholic beverages during pregnancy because of the risk of birth "
    "defects. (2) Consumption of alcoholic beverages impairs your ability to drive "
    "a car or operate machinery, and may cause health problems."
)

WARNING_PLACEHOLDER_TEXT = "Placeholder warning text requires OCR validation"
ALCOHOL_PATTERN = re.compile(r"(abv\b|alc\.?\s*/?\s*vol|proof\b)", re.IGNORECASE)
NET_CONTENTS_PATTERN = re.compile(r"(ml|fl\s*oz|floz)", re.IGNORECASE)
WARNING_END_PATTERN = re.compile(r"health problems[.!?]?", re.IGNORECASE)

BRAND_CLASS_REVIEW_THRESHOLD = 0.92
NET_CONTENTS_REVIEW_THRESHOLD = 0.90
WARNING_REVIEW_THRESHOLD = 0.97

def build_verification_result(
    *,
    original_name,
    mime_type,
    size_bytes,
    brand_name,
    class_type,
    alcohol_content,
    net_contents,
    ocr_lines,
    ocr_error=None,
):
    expected_fields = {
        "brandName": normalize_value(brand_name),
        "classType": normalize_value(class_type),
        "alcoholContent": normalize_value(alcohol_content),
        "netContents": normalize_value(net_contents),
        "governmentWarning": STANDARD_GOVERNMENT_WARNING,
    }
    detected_fields = build_ocr_detected_fields(expected_fields, ocr_lines)
    results = build_verification_results(expected_fields, detected_fields)
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
        "placeholder": False,
        "note": build_verification_note(results, ocr_error),
    }


def build_warning_result(field_definition, expected_value, detected_value):
    if not detected_value:
        return {
            "field": field_definition["label"],
            "expectedValue": expected_value,
            "detectedValue": "",
            "status": "Mismatch",
            "notes": "Required warning text was not detected.",
        }

    if not detected_value.startswith("GOVERNMENT WARNING:"):
        return {
            "field": field_definition["label"],
            "expectedValue": expected_value,
            "detectedValue": detected_value,
            "status": "Mismatch",
            "notes": "Detected warning does not use the uppercase 'GOVERNMENT WARNING:' prefix.",
        }

    if normalize_warning_text_for_comparison(expected_value) == normalize_warning_text_for_comparison(detected_value):
        return {
            "field": field_definition["label"],
            "expectedValue": expected_value,
            "detectedValue": detected_value,
            "status": "Match",
            "notes": "Matched exactly from OCR text.",
        }

    if similarity_ratio(expected_value, detected_value) >= WARNING_REVIEW_THRESHOLD:
        return {
            "field": field_definition["label"],
            "expectedValue": expected_value,
            "detectedValue": detected_value,
            "status": "Needs Review",
            "notes": "Warning text is close to the expected wording but does not match exactly, including case.",
        }

    return {
        "field": field_definition["label"],
        "expectedValue": expected_value,
        "detectedValue": detected_value,
        "status": "Mismatch",
        "notes": "Detected warning text differs from the expected wording.",
    }


def build_verification_note(results, ocr_error):
    if ocr_error:
        return f"OCR could not be completed: {ocr_error}"

    if any(result["status"] == "Needs Review" for result in results):
        return "OCR-based verification completed. Review fields marked Needs Review."

    return "OCR-based verification completed."


def build_verification_results(expected_fields, detected_fields):
    results = []

    for field_definition in FIELD_DEFINITIONS:
        field_key = field_definition["key"]
        expected_value = expected_fields[field_key]
        detected_value = detected_fields[field_key]
        results.append(
            build_verification_result_row(
                field_definition,
                expected_value,
                detected_value,
            )
        )

    return results


def build_verification_result_row(field_definition, expected_value, detected_value):
    field_key = field_definition["key"]

    if not expected_value:
        return {
            "field": field_definition["label"],
            "expectedValue": "",
            "detectedValue": detected_value,
            "status": "Needs Review",
            "notes": "No expected value provided.",
        }

    if field_key == "governmentWarning":
        return build_warning_result(field_definition, expected_value, detected_value)

    if not detected_value:
        return {
            "field": field_definition["label"],
            "expectedValue": expected_value,
            "detectedValue": "",
            "status": "Needs Review",
            "notes": "OCR could not confidently extract this field.",
        }

    normalized_match = compact_field_value(field_key, expected_value) == compact_field_value(
        field_key,
        detected_value,
    )
    similarity = similarity_ratio(expected_value, detected_value)

    if normalized_match:
        return {
            "field": field_definition["label"],
            "expectedValue": expected_value,
            "detectedValue": detected_value,
            "status": "Match",
            "notes": "Matched from OCR text.",
        }

    if field_key in {"brandName", "classType"}:
        if similarity >= BRAND_CLASS_REVIEW_THRESHOLD:
            return {
                "field": field_definition["label"],
                "expectedValue": expected_value,
                "detectedValue": detected_value,
                "status": "Needs Review",
                "notes": "OCR text is close to the expected value but contains character differences.",
            }

    if field_key == "netContents":
        if similarity >= NET_CONTENTS_REVIEW_THRESHOLD:
            return {
                "field": field_definition["label"],
                "expectedValue": expected_value,
                "detectedValue": detected_value,
                "status": "Needs Review",
                "notes": "OCR text is close to the expected net contents but not exact.",
            }

    return {
        "field": field_definition["label"],
        "expectedValue": expected_value,
        "detectedValue": detected_value,
        "status": "Mismatch",
        "notes": "Detected text does not match the expected value.",
    }


# Summarizes the results for the UI header.
def summarize_results(results):
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


# Trims text input so blank and whitespace-only values are handled consistently
def normalize_value(value):
    return value.strip() if isinstance(value, str) else ""


# Removes extra whitespace and newlines from OCR lines for better matching and extraction
def normalize_whitespace(value):
    return " ".join(value.strip().split())


# Normalizes minor trailing punctuation differences in OCR warning text.
def normalize_warning_text_for_comparison(value):
    normalized = normalize_whitespace(value)
    return re.sub(r"[.!?]+$", "", normalized)


# Normalizes common OCR variations in net contents units before matching.
def normalize_net_contents_candidate(value):
    normalized = value.upper().strip()
    normalized = re.sub(r"FL\s*[0O]\s*Z", "FL OZ", normalized)
    normalized = re.sub(r"(\d)(FL\s*OZ\b)", r"\1 \2", normalized)
    normalized = re.sub(r"(\d)(ML\b)", r"\1 ML", normalized)
    return normalized


def normalize_alcohol_content_candidate(value):
    normalized = value.upper().strip()
    normalized = re.sub(r"(?<=\d)%(?=[A-Z])", "% ", normalized)
    normalized = re.sub(r"\bABV\b", "ALC/VOL", normalized)
    normalized = re.sub(r"ALC\.?\s*/?\s*VOL\.?", "ALC/VOL", normalized)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized


# Compacts a value by removing non-alphanumeric characters for better similarity comparison
def compact_value(value):
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def compact_field_value(field_key, value):
    if field_key == "alcoholContent":
        value = normalize_alcohol_content_candidate(value)
    elif field_key == "netContents":
        value = normalize_net_contents_candidate(value)

    return compact_value(value)


# Computes a similarity ratio between expected and detected values for better matching of OCR spans
def similarity_ratio(expected_value, detected_value):
    return SequenceMatcher(
        None,
        compact_value(expected_value),
        compact_value(detected_value),
    ).ratio()


# Selects the best contiguous span of OCR lines that matches the expected value based on similarity ratio
def select_best_span(expected_value, ocr_lines, max_size=3):
    if not expected_value or not ocr_lines:
        return ""

    best_candidate = ""
    best_score = -1.0

    for span_size in range(1, max_size + 1):
        for start_index in range(0, len(ocr_lines) - span_size + 1):
            candidate = " ".join(ocr_lines[start_index : start_index + span_size])
            score = similarity_ratio(expected_value, candidate)

            if score > best_score:
                best_candidate = candidate
                best_score = score

    return best_candidate


# Extraction functions for specific fields using regex patterns
def extract_alcohol_content(ocr_lines):
    matched_lines = [line for line in ocr_lines if ALCOHOL_PATTERN.search(line)]
    return " ".join(matched_lines[:2]).strip()


# Similar regex-based extraction for net contents, looking for common units like ml and fl oz
def extract_net_contents(ocr_lines):
    for line in ocr_lines:
        normalized_line = normalize_net_contents_candidate(line)
        if NET_CONTENTS_PATTERN.search(normalized_line):
            return normalized_line

    return ""


# Extracts the government warning by finding the first line that contains "warning"
# and stopping once the warning's ending phrase is reached.
def extract_government_warning(ocr_lines):
    for index, line in enumerate(ocr_lines):
        if "warning" in line.lower():
            warning_lines = []

            for candidate_line in ocr_lines[index:]:
                warning_lines.append(candidate_line)
                if WARNING_END_PATTERN.search(candidate_line):
                    break

            warning_text = " ".join(warning_lines).strip()
            warning_end_match = WARNING_END_PATTERN.search(warning_text)
            if warning_end_match:
                return warning_text[: warning_end_match.end()].strip()

            return warning_text

    return ""


# Cleans lines and builds detected fields
def build_ocr_detected_fields(expected_fields, ocr_lines):
    
    cleaned_lines = [normalize_whitespace(line) for line in ocr_lines if line.strip()]

    return {
        "brandName": select_best_span(expected_fields["brandName"], cleaned_lines),
        "classType": select_best_span(expected_fields["classType"], cleaned_lines),
        "alcoholContent": extract_alcohol_content(cleaned_lines),
        "netContents": extract_net_contents(cleaned_lines),
        "governmentWarning": extract_government_warning(cleaned_lines),
    }
