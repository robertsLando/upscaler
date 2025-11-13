"""
Unit tests for the upscaler module.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from PIL import Image

from upscaler.upscaler import cm_to_pixels, resize_to_target


class TestCmToPixels:
    """Tests for the cm_to_pixels function."""

    def test_basic_conversion(self):
        """Test basic cm to pixels conversion."""
        # 10cm x 10cm at 300 DPI
        width_px, height_px = cm_to_pixels(10, 10, 300)
        # 10cm / 2.54 = 3.937 inches, 3.937 * 300 = 1181.1 pixels, rounded = 1181
        assert width_px == 1181
        assert height_px == 1181

    def test_a4_size_300dpi(self):
        """Test A4 paper size conversion at 300 DPI."""
        # A4 is approximately 21 x 29.7 cm
        width_px, height_px = cm_to_pixels(21, 29.7, 300)
        # 21cm / 2.54 = 8.268 inches, 8.268 * 300 = 2480.4 pixels, rounded = 2480
        # 29.7cm / 2.54 = 11.693 inches, 11.693 * 300 = 3507.9 pixels, rounded = 3508
        assert width_px == 2480
        assert height_px == 3508

    def test_small_dimensions(self):
        """Test small dimensions conversion."""
        # 1cm x 1cm at 72 DPI (screen resolution)
        width_px, height_px = cm_to_pixels(1, 1, 72)
        # 1cm / 2.54 = 0.394 inches, 0.394 * 72 = 28.35 pixels, rounded = 28
        assert width_px == 28
        assert height_px == 28

    def test_high_dpi(self):
        """Test conversion with high DPI."""
        # 5cm x 5cm at 600 DPI
        width_px, height_px = cm_to_pixels(5, 5, 600)
        # 5cm / 2.54 = 1.969 inches, 1.969 * 600 = 1181.4 pixels, rounded = 1181
        assert width_px == 1181
        assert height_px == 1181

    def test_different_dimensions(self):
        """Test conversion with different width and height."""
        # 15cm x 10cm at 150 DPI
        width_px, height_px = cm_to_pixels(15, 10, 150)
        # 15cm / 2.54 = 5.906 inches, 5.906 * 150 = 885.9 pixels, rounded = 886
        # 10cm / 2.54 = 3.937 inches, 3.937 * 150 = 590.55 pixels, rounded = 591
        assert width_px == 886
        assert height_px == 591

    def test_returns_integers(self):
        """Test that function returns integers."""
        width_px, height_px = cm_to_pixels(7.5, 12.3, 200)
        assert isinstance(width_px, int)
        assert isinstance(height_px, int)


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

    def test_resize_real_image(self, panda_pil_image):
        """Test resizing the real panda test image."""
        # Load real test image
        img = panda_pil_image
        original_size = img.size

        # Resize to 800x800
        result = resize_to_target(img, 800, 800)

        # Should maintain aspect ratio and fit within 800x800
        assert result.size[0] <= 800
        assert result.size[1] <= 800
        # At least one dimension should be 800 (or close due to aspect ratio)
        assert max(result.size) >= 700

        # Verify the image was actually resized
        assert result.size != original_size

        # Verify it's still an RGB image
        assert result.mode == "RGB"
