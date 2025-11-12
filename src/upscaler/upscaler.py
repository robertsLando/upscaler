"""
Core upscaling functionality using Real-ESRGAN.
"""

import logging

from PIL import Image

logger = logging.getLogger(__name__)

# Initialize Real-ESRGAN upsampler lazily to avoid startup delays
_upsampler = None


def get_upsampler():
    """
    Lazy initialization of Real-ESRGAN model.

    Returns:
        RealESRGANer: Initialized upsampler instance
    """
    global _upsampler
    if _upsampler is None:
        try:
            # Import torch dependencies only when needed
            import sys

            import torchvision.transforms.functional as F

            # Patch for torchvision compatibility with basicsr
            # basicsr expects torchvision.transforms.functional_tensor which was renamed
            sys.modules["torchvision.transforms.functional_tensor"] = F

            from basicsr.archs.rrdbnet_arch import RRDBNet
            from realesrgan import RealESRGANer

            logger.info("Initializing Real-ESRGAN model...")

            # Use RealESRGAN_x4plus model
            model = RRDBNet(
                num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4
            )

            # Initialize upsampler - it will download the model automatically
            _upsampler = RealESRGANer(
                scale=4,
                model_path="https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth",
                model=model,
                tile=0,
                tile_pad=10,
                pre_pad=0,
                half=False,  # Use FP32 for CPU compatibility
                gpu_id=None,  # Use CPU
            )
            logger.info("Real-ESRGAN model initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Real-ESRGAN: {e}")
            raise
    return _upsampler


def resize_to_target(image: Image.Image, target_width: int, target_height: int) -> Image.Image:
    """
    Resize image to target dimensions while preserving aspect ratio.
    The image will fit within the target dimensions.

    Args:
        image: PIL Image to resize
        target_width: Target width in pixels
        target_height: Target height in pixels

    Returns:
        PIL Image resized to fit within target dimensions
    """
    original_width, original_height = image.size

    # Calculate aspect ratios
    target_ratio = target_width / target_height
    original_ratio = original_width / original_height

    # Determine new size maintaining aspect ratio
    if original_ratio > target_ratio:
        # Width is the limiting factor
        new_width = target_width
        new_height = int(target_width / original_ratio)
    else:
        # Height is the limiting factor
        new_height = target_height
        new_width = int(target_height * original_ratio)

    return image.resize((new_width, new_height), Image.LANCZOS)
