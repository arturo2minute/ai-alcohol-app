import os

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.ocr import OCRExtractionError, extract_text_lines
from app.verifier import build_verification_result

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
    # Ensure an image was uploaded and is 10 MB or smaller.
    if image is None or not image.filename:
        return JSONResponse(
            status_code=400,
            content={"error": "An image file is required."},
        )

    file_bytes = await image.read()

    if len(file_bytes) > 10 * 1024 * 1024:
        return JSONResponse(
            status_code=400,
            content={"error": "Image file must be 10 MB or smaller."},
        )

    try:
        ocr_lines = extract_text_lines(file_bytes)
        ocr_error = None
    except OCRExtractionError as exc:
        ocr_lines = []
        ocr_error = str(exc)

    return build_verification_result(
        original_name=image.filename,
        mime_type=image.content_type,
        size_bytes=len(file_bytes),
        brand_name=brandName,
        class_type=classType,
        alcohol_content=alcoholContent,
        net_contents=netContents,
        ocr_lines=ocr_lines,
        ocr_error=ocr_error,
    )
