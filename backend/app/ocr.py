from functools import lru_cache


class OCRExtractionError(RuntimeError):
    """Raised when OCR cannot be run on an image payload."""


@lru_cache(maxsize=1)
def get_ocr_engine():
    try:
        from rapidocr_onnxruntime import RapidOCR
    except ImportError as exc:
        raise OCRExtractionError(
            "OCR dependency is not installed in the backend environment."
        ) from exc

    return RapidOCR()


def extract_text_lines(file_bytes):
    try:
        import cv2
        import numpy as np
    except ImportError as exc:
        raise OCRExtractionError(
            "OCR image dependencies are not installed in the backend environment."
        ) from exc

    image_array = np.frombuffer(file_bytes, dtype=np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    if image is None:
        raise OCRExtractionError("The uploaded file could not be decoded as an image.")

    try:
        result, _ = get_ocr_engine()(image)
    except Exception as exc:  # pragma: no cover
        raise OCRExtractionError(f"OCR extraction failed: {exc}") from exc

    return [
        str(entry[1]).strip()
        for entry in (result or [])
        if len(entry) >= 2 and str(entry[1]).strip()
    ]
