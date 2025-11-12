"""
Image upscaler package using Real-ESRGAN.
"""

from .app import app
from .upscaler import get_upsampler, resize_to_target

__all__ = ["app", "get_upsampler", "resize_to_target"]
