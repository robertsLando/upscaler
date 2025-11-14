"""
Image upscaler web application using FastAPI and Real-ESRGAN.
"""

import io
import logging
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image

from .upscaler import cm_to_pixels
from .utils import upscale_image as upscale_image_util

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Image Upscaler API", description="Upscale images using Real-ESRGAN")

# Get the templates and static directories
TEMPLATES_DIR = Path(__file__).parent / "templates"
STATIC_DIR = Path(__file__).parent / "static"

# Mount static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
async def root():
    """Serve the HTML UI"""
    index_file = TEMPLATES_DIR / "index.html"
    return FileResponse(index_file)


@app.post("/upscale")
async def upscale_image(
    image: UploadFile = File(...),
    target_width: int = Form(None),
    target_height: int = Form(None),
    width_cm: float = Form(None),
    height_cm: float = Form(None),
    dpi: int = Form(None),
):
    """
    Upscale an image to target dimensions using Real-ESRGAN.
    The aspect ratio is preserved.

    You can specify dimensions in two ways:
    1. Directly in pixels using target_width and target_height
    2. In centimeters and DPI using width_cm, height_cm, and dpi

    Args:
        image: Image file to upscale
        target_width: Target width in pixels (1-10000) - used if width_cm is not provided
        target_height: Target height in pixels (1-10000) - used if height_cm is not provided
        width_cm: Target width in centimeters (0.1-400) - alternative to target_width
        height_cm: Target height in centimeters (0.1-400) - alternative to target_height
        dpi: Dots per inch (10-1200) - required when using width_cm/height_cm

    Returns:
        StreamingResponse with the upscaled image as PNG
    """
    # Determine which input method to use
    if width_cm is not None or height_cm is not None or dpi is not None:
        # Using cm/dpi mode
        if width_cm is None or height_cm is None or dpi is None:
            raise HTTPException(
                status_code=400,
                detail="When using cm/dpi mode, all three parameters (width_cm, height_cm, dpi) are required",
            )

        # Validate cm dimensions
        if width_cm < 0.1 or width_cm > 400:
            raise HTTPException(
                status_code=400, detail="Width must be between 0.1 and 400 centimeters"
            )
        if height_cm < 0.1 or height_cm > 400:
            raise HTTPException(
                status_code=400, detail="Height must be between 0.1 and 400 centimeters"
            )

        # Validate DPI
        if dpi < 10 or dpi > 1200:
            raise HTTPException(status_code=400, detail="DPI must be between 10 and 1200")

        # Convert cm to pixels
        target_width, target_height = cm_to_pixels(width_cm, height_cm, dpi)
        logger.info(
            f"Converted {width_cm}cm x {height_cm}cm @ {dpi}dpi to {target_width}px x {target_height}px"
        )
    else:
        # Using pixel mode
        if target_width is None or target_height is None:
            raise HTTPException(
                status_code=400,
                detail="Either provide target_width and target_height (in pixels) or width_cm, height_cm, and dpi",
            )

    # Validate pixel dimensions
    if target_width < 1 or target_width > 10000:
        raise HTTPException(status_code=400, detail="Width must be between 1 and 10000 pixels")
    if target_height < 1 or target_height > 10000:
        raise HTTPException(status_code=400, detail="Height must be between 1 and 10000 pixels")

    # Check file type
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    try:
        # Read the uploaded image
        contents = await image.read()
        img = Image.open(io.BytesIO(contents))

        # Upscale the image using shared utility function
        final_img = upscale_image_util(img, target_width, target_height)

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
