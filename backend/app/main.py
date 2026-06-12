import os
from typing import Optional

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.verifier import build_placeholder_verification

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
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "ai-alcohol-app-backend"}


# Placeholder verification endpoint. It accepts the uploaded image and form fields,
# then returns fake results until OCR and real extraction are implemented.
@app.post("/verify")
async def verify(
    image: Optional[UploadFile] = File(default=None),
    brandName: Optional[str] = Form(default=""),
    classType: Optional[str] = Form(default=""),
    alcoholContent: Optional[str] = Form(default=""),
    netContents: Optional[str] = Form(default=""),
    governmentWarning: Optional[str] = Form(default=""),
) -> dict:
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

    return build_placeholder_verification(
        original_name=image.filename,
        mime_type=image.content_type,
        size_bytes=len(file_bytes),
        brand_name=brandName,
        class_type=classType,
        alcohol_content=alcoholContent,
        net_contents=netContents,
        government_warning=governmentWarning,
    )
