"""
Utility functions for image upscaling operations.
"""

import logging

import numpy as np
from PIL import Image

from .upscaler import get_upsampler, resize_to_target

logger = logging.getLogger(__name__)


def upscale_image(img: Image.Image, target_width: int, target_height: int) -> Image.Image:
    """
    Upscale an image to target dimensions using Real-ESRGAN.

    This function contains the core upscaling logic used by both the API and CLI.
    It converts the image to RGB, upscales it 4x using Real-ESRGAN, and then
    resizes to the target dimensions while preserving aspect ratio.

    Args:
        img: PIL Image to upscale (will be converted to RGB if needed)
        target_width: Target width in pixels
        target_height: Target height in pixels

    Returns:
        PIL Image upscaled and resized to target dimensions

    Raises:
        Exception: If upscaling fails
    """
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
    logger.info(f"Upscaled to: {output.shape[:2][::-1]}")

    # Convert back to PIL Image
    upscaled_img = Image.fromarray(output)

    # Resize to target dimensions while preserving aspect ratio
    final_img = resize_to_target(upscaled_img, target_width, target_height)
    logger.info(f"Final image size: {final_img.size}")

    return final_img
