import logging
import os
import time

from fastapi import FastAPI, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.ocr import (
    OCRExtractionError,
    decode_image,
    extract_text_lines_from_image,
    resize_for_ocr,
)
from app.verifier import assemble_verification_response, build_verification_artifacts


logger = logging.getLogger("uvicorn.error")

# FastAPI application setup.
app = FastAPI(title="AI Alcohol App Backend")

# Allowed frontend origins for local development.
allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "FRONTEND_ORIGIN", "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Simple health endpoint so the frontend can confirm the API is reachable.
@app.get("/health")
async def health():
    return {"status": "ok", "service": "ai-alcohol-app-backend"}


# Verification endpoint. It accepts the uploaded image and form fields,
# extracts OCR text, and applies deterministic comparison rules.
@app.post("/verify")
async def verify(
    image=File(default=None),
    brandName=Form(default=""),
    classType=Form(default=""),
    alcoholContent=Form(default=""),
    netContents=Form(default=""),
):
    request_started_at = time.perf_counter()
    filename = image.filename if image is not None and image.filename else "<missing>"
    logger.info("[verify timing] request_start filename=%s", filename)

    # Ensure an image was uploaded and is 10 MB or smaller.
    if image is None or not image.filename:
        return JSONResponse(
            status_code=400,
            content={"error": "An image file is required."},
        )

    try:
        file_read_started_at = time.perf_counter()
        file_bytes = await image.read()
        file_read_time = time.perf_counter() - file_read_started_at

        if len(file_bytes) > 10 * 1024 * 1024:
            return JSONResponse(
                status_code=400,
                content={"error": "Image file must be 10 MB or smaller."},
            )

        image_decode_time = 0.0
        preprocessing_time = 0.0
        ocr_time = 0.0
        validation_time = 0.0
        response_assembly_time = 0.0
        ocr_error = None
        ocr_lines = []
        original_dimensions = None
        resized_dimensions = None

        try:
            image_decode_started_at = time.perf_counter()
            decoded_image = decode_image(file_bytes)
            image_decode_time = time.perf_counter() - image_decode_started_at

            preprocessing_started_at = time.perf_counter()
            processed_image, original_dimensions, resized_dimensions = resize_for_ocr(
                decoded_image
            )
            preprocessing_time = time.perf_counter() - preprocessing_started_at

            logger.info(
                "[verify image] original=%sx%s resized=%sx%s",
                original_dimensions[0],
                original_dimensions[1],
                resized_dimensions[0],
                resized_dimensions[1],
            )

            ocr_started_at = time.perf_counter()
            ocr_lines = extract_text_lines_from_image(processed_image)
            ocr_time = time.perf_counter() - ocr_started_at
        except OCRExtractionError as exc:
            ocr_error = str(exc)
            logger.warning("[verify ocr] error=%s", ocr_error)

        validation_started_at = time.perf_counter()
        verification_artifacts = build_verification_artifacts(
            brand_name=brandName,
            class_type=classType,
            alcohol_content=alcoholContent,
            net_contents=netContents,
            ocr_lines=ocr_lines,
            ocr_error=ocr_error,
        )
        validation_time = time.perf_counter() - validation_started_at

        response_assembly_started_at = time.perf_counter()
        response_payload = assemble_verification_response(
            original_name=image.filename,
            mime_type=image.content_type,
            size_bytes=len(file_bytes),
            expected_fields=verification_artifacts["expectedFields"],
            results=verification_artifacts["results"],
            summary=verification_artifacts["summary"],
            note=verification_artifacts["note"],
        )
        response_assembly_time = time.perf_counter() - response_assembly_started_at

        total_time = time.perf_counter() - request_started_at
        logger.info(
            "[verify timing] file_read=%.4fs image_decode=%.4fs preprocessing=%.4fs "
            "ocr=%.4fs validation=%.4fs response_assembly=%.4fs total=%.4fs",
            file_read_time,
            image_decode_time,
            preprocessing_time,
            ocr_time,
            validation_time,
            response_assembly_time,
            total_time,
        )

        return response_payload
    except Exception as exc:
        total_time = time.perf_counter() - request_started_at
        logger.exception(
            "[verify error]exception_type=%s exception=%s total=%.4fs",
            type(exc).__name__,
            exc,
            total_time,
        )
        return JSONResponse(
            status_code=500,
            content={"error": "Verification could not be completed."},
        )
