"""
Tests for the utils module.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from PIL import Image

from upscaler.utils import upscale_image


class TestUpscaleImage:
    """Tests for the upscale_image function."""

    def test_upscale_rgb_image(self):
        """Test upscaling a normal RGB image."""
        img = Image.new("RGB", (100, 100), color="red")
        result = upscale_image(img, 400, 400)

        assert result.size == (400, 400)
        assert result.mode == "RGB"

    def test_upscale_non_rgb_image(self):
        """Test that non-RGB images are converted."""
        img = Image.new("RGBA", (100, 100), color=(255, 0, 0, 128))
        result = upscale_image(img, 400, 400)

        # Should be converted to RGB
        assert result.mode == "RGB"
        assert result.size == (400, 400)

    def test_upscale_preserves_aspect_ratio(self):
        """Test that aspect ratio is preserved."""
        # Create a wide image (2:1 aspect ratio)
        img = Image.new("RGB", (200, 100), color="blue")
        result = upscale_image(img, 800, 600)

        # Should be 800x400 (limited by width)
        assert result.size == (800, 400)

    def test_upscale_tall_image(self):
        """Test upscaling a tall image."""
        # Create a tall image (1:2 aspect ratio)
        img = Image.new("RGB", (100, 200), color="green")
        result = upscale_image(img, 600, 800)

        # Should be 400x800 (limited by height)
        assert result.size == (400, 800)
