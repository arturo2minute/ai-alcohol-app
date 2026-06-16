import logging
from functools import lru_cache


logger = logging.getLogger("uvicorn.error")


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

    # The OCR engine is cached so it is initialized once and reused across requests.
    logger.info("Initializing RapidOCR engine")
    return RapidOCR()


def decode_image(file_bytes):
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

    return image


def resize_for_ocr(image, max_width=1600):
    try:
        import cv2
    except ImportError as exc:
        raise OCRExtractionError(
            "OCR image dependencies are not installed in the backend environment."
        ) from exc

    height, width = image.shape[:2]

    if width <= max_width:
        return image, (width, height), (width, height)

    scale = max_width / float(width)
    resized_height = max(1, int(round(height * scale)))
    resized_image = cv2.resize(
        image,
        (max_width, resized_height),
        interpolation=cv2.INTER_AREA,
    )
    return resized_image, (width, height), (max_width, resized_height)


def extract_text_lines_from_image(image):
    try:
        result, _ = get_ocr_engine()(image)
    except Exception as exc:  # pragma: no cover
        raise OCRExtractionError(f"OCR extraction failed: {exc}") from exc

    return [
        str(entry[1]).strip()
        for entry in (result or [])
        if len(entry) >= 2 and str(entry[1]).strip()
    ]


def extract_text_lines(file_bytes):
    image = decode_image(file_bytes)
    resized_image, _, _ = resize_for_ocr(image)
    return extract_text_lines_from_image(resized_image)
