"""
Image upscaler web application using FastAPI and Real-ESRGAN.
"""

import io
import logging
from pathlib import Path

import numpy as np
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from PIL import Image

from .upscaler import get_upsampler, resize_to_target

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Image Upscaler API", description="Upscale images using Real-ESRGAN")

# Get the templates directory
TEMPLATES_DIR = Path(__file__).parent / "templates"


@app.get("/")
async def root():
    """Serve the HTML UI"""
    index_file = TEMPLATES_DIR / "index.html"
    return FileResponse(index_file)


@app.post("/upscale")
async def upscale_image(
    image: UploadFile = File(...), target_width: int = Form(...), target_height: int = Form(...)
):
    """
    Upscale an image to target dimensions using Real-ESRGAN.
    The aspect ratio is preserved.

    Args:
        image: Image file to upscale
        target_width: Target width in pixels (1-4096)
        target_height: Target height in pixels (1-4096)

    Returns:
        StreamingResponse with the upscaled image as PNG
    """
    # Validate inputs
    if target_width < 1 or target_width > 4096:
        raise HTTPException(status_code=400, detail="Width must be between 1 and 4096 pixels")
    if target_height < 1 or target_height > 4096:
        raise HTTPException(status_code=400, detail="Height must be between 1 and 4096 pixels")

    # Check file type
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    try:
        # Read the uploaded image
        contents = await image.read()
        img = Image.open(io.BytesIO(contents))

        # Convert to RGB if necessary
        if img.mode != "RGB":
            img = img.convert("RGB")

        logger.info(f"Original image size: {img.size}")

        # Get upsampler
        upsampler = get_upsampler()

        # Convert PIL Image to numpy array
        img_np = np.array(img)

        # Upscale with Real-ESRGAN
        logger.info("Starting upscaling process...")
        output, _ = upsampler.enhance(img_np, outscale=4)
        logger.info(f"Upscaled to: {output.shape}")

        # Convert back to PIL Image
        upscaled_img = Image.fromarray(output)

        # Resize to target dimensions while preserving aspect ratio
        final_img = resize_to_target(upscaled_img, target_width, target_height)
        logger.info(f"Final image size: {final_img.size}")

        # Save to bytes buffer
        img_byte_arr = io.BytesIO()
        final_img.save(img_byte_arr, format="PNG")
        img_byte_arr.seek(0)

        return StreamingResponse(
            img_byte_arr,
            media_type="image/png",
            headers={"Content-Disposition": f"attachment; filename=upscaled_{image.filename}"},
        )

    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Image upscaler API is running"}
