"""
Unit tests for the upscaler module.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from PIL import Image

from upscaler.upscaler import resize_to_target


class TestResizeToTarget:
    """Tests for the resize_to_target function."""

    def test_resize_wider_image(self):
        """Test resizing a wider image maintains aspect ratio."""
        # Create a 200x100 image (2:1 aspect ratio)
        img = Image.new("RGB", (200, 100), color="red")

        # Resize to fit in 400x400
        result = resize_to_target(img, 400, 400)

        # Should be 400x200 to maintain aspect ratio
        assert result.size == (400, 200)

    def test_resize_taller_image(self):
        """Test resizing a taller image maintains aspect ratio."""
        # Create a 100x200 image (1:2 aspect ratio)
        img = Image.new("RGB", (100, 200), color="blue")

        # Resize to fit in 400x400
        result = resize_to_target(img, 400, 400)

        # Should be 200x400 to maintain aspect ratio
        assert result.size == (200, 400)

    def test_resize_square_image(self):
        """Test resizing a square image."""
        # Create a 100x100 image
        img = Image.new("RGB", (100, 100), color="green")

        # Resize to fit in 500x500
        result = resize_to_target(img, 500, 500)

        # Should be 500x500
        assert result.size == (500, 500)

    def test_resize_maintains_content(self):
        """Test that resizing maintains image content."""
        # Create a simple test pattern
        img = Image.new("RGB", (100, 100), color="white")
        pixels = img.load()
        for i in range(50):
            for j in range(50):
                pixels[i, j] = (255, 0, 0)  # Red square in top-left

        # Resize
        result = resize_to_target(img, 200, 200)

        # Check that we still have red in top-left area
        result_pixels = result.load()
        # Sample a few pixels in top-left quadrant
        assert result_pixels[10, 10][0] > 200  # Should be reddish
        assert result_pixels[10, 10][1] < 50  # Low green
        assert result_pixels[10, 10][2] < 50  # Low blue

    def test_resize_to_non_square_target(self):
        """Test resizing to non-square target dimensions."""
        # Create a square 100x100 image
        img = Image.new("RGB", (100, 100), color="yellow")

        # Resize to fit in 800x400 (2:1 target)
        result = resize_to_target(img, 800, 400)

        # Should be 400x400 (limited by height)
        assert result.size == (400, 400)

    def test_resize_with_different_aspect_ratios(self):
        """Test various aspect ratio combinations."""
        # 16:9 image into 4:3 target
        img = Image.new("RGB", (1600, 900), color="purple")
        result = resize_to_target(img, 800, 600)

        # Should be 800x450 (limited by width)
        assert result.size == (800, 450)

        # 4:3 image into 16:9 target
        img2 = Image.new("RGB", (400, 300), color="orange")
        result2 = resize_to_target(img2, 1920, 1080)

        # Should be 1440x1080 (limited by height)
        assert result2.size == (1440, 1080)
