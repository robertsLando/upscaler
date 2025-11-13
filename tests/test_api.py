"""
API integration tests for the upscaler application.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import io

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from upscaler import app

client = TestClient(app)


class TestHealthEndpoint:
    """Tests for the health check endpoint."""

    def test_health_check(self):
        """Test that health check returns 200 OK."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "message" in data


class TestRootEndpoint:
    """Tests for the root endpoint."""

    def test_root_returns_html(self):
        """Test that root endpoint returns HTML."""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert b"Image Upscaler" in response.content


class TestUpscaleEndpoint:
    """Tests for the upscale endpoint."""

    def create_test_image(self, width=100, height=100, color="red"):
        """Helper to create a test image."""
        img = Image.new("RGB", (width, height), color=color)
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="JPEG")
        img_bytes.seek(0)
        return img_bytes

    def load_test_image(self):
        """Load the real test image (panda-low.jpeg)."""
        test_image_path = Path(__file__).parent / "assets" / "panda-low.jpeg"
        with open(test_image_path, "rb") as f:
            return io.BytesIO(f.read())

    def test_upscale_requires_image(self):
        """Test that upscale endpoint requires an image."""
        response = client.post("/upscale", data={"target_width": 400, "target_height": 400})
        assert response.status_code == 422  # Unprocessable Entity

    def test_upscale_requires_dimensions(self):
        """Test that upscale endpoint requires dimensions."""
        img_bytes = self.create_test_image()
        response = client.post("/upscale", files={"image": ("test.jpg", img_bytes, "image/jpeg")})
        assert response.status_code == 400  # Bad Request - no dimensions provided

    def test_upscale_validates_width_range(self):
        """Test that width is validated."""
        img_bytes = self.create_test_image()

        # Test width too small
        response = client.post(
            "/upscale",
            files={"image": ("test.jpg", img_bytes, "image/jpeg")},
            data={"target_width": 0, "target_height": 400},
        )
        assert response.status_code == 400

        # Test width too large
        img_bytes = self.create_test_image()
        response = client.post(
            "/upscale",
            files={"image": ("test.jpg", img_bytes, "image/jpeg")},
            data={"target_width": 11000, "target_height": 400},
        )
        assert response.status_code == 400

    def test_upscale_validates_height_range(self):
        """Test that height is validated."""
        img_bytes = self.create_test_image()

        # Test height too small
        response = client.post(
            "/upscale",
            files={"image": ("test.jpg", img_bytes, "image/jpeg")},
            data={"target_width": 400, "target_height": 0},
        )
        assert response.status_code == 400

        # Test height too large
        img_bytes = self.create_test_image()
        response = client.post(
            "/upscale",
            files={"image": ("test.jpg", img_bytes, "image/jpeg")},
            data={"target_width": 400, "target_height": 11000},
        )
        assert response.status_code == 400

    def test_upscale_rejects_non_image(self):
        """Test that non-image files are rejected."""
        # Create a text file
        text_file = io.BytesIO(b"This is not an image")

        response = client.post(
            "/upscale",
            files={"image": ("test.txt", text_file, "text/plain")},
            data={"target_width": 400, "target_height": 400},
        )
        assert response.status_code == 400

    @pytest.mark.slow
    def test_upscale_success(self):
        """Test successful image upscaling with real panda image (slow test, requires model)."""
        # Load the real test image
        img_bytes = self.load_test_image()

        response = client.post(
            "/upscale",
            files={"image": ("panda-low.jpeg", img_bytes, "image/jpeg")},
            data={"target_width": 512, "target_height": 512},
        )

        # This test requires the Real-ESRGAN model to be initialized
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        assert response.headers["content-type"] == "image/png"
        # Verify we got an image back
        output_img = Image.open(io.BytesIO(response.content))
        assert output_img.size[0] <= 512
        assert output_img.size[1] <= 512
        # Verify it's actually upscaled (should be larger than original low-res image)
        assert output_img.size[0] > 100  # Should be significantly larger than tiny dimensions

    def test_upscale_with_cm_dpi_requires_all_params(self):
        """Test that cm/dpi mode requires all three parameters."""
        img_bytes = self.create_test_image()

        # Missing dpi
        response = client.post(
            "/upscale",
            files={"image": ("test.jpg", img_bytes, "image/jpeg")},
            data={"width_cm": 10, "height_cm": 10},
        )
        assert response.status_code == 400

        # Missing height_cm
        img_bytes = self.create_test_image()
        response = client.post(
            "/upscale",
            files={"image": ("test.jpg", img_bytes, "image/jpeg")},
            data={"width_cm": 10, "dpi": 300},
        )
        assert response.status_code == 400

        # Missing width_cm
        img_bytes = self.create_test_image()
        response = client.post(
            "/upscale",
            files={"image": ("test.jpg", img_bytes, "image/jpeg")},
            data={"height_cm": 10, "dpi": 300},
        )
        assert response.status_code == 400

    def test_upscale_validates_cm_range(self):
        """Test that cm dimensions are validated."""
        img_bytes = self.create_test_image()

        # Width too small
        response = client.post(
            "/upscale",
            files={"image": ("test.jpg", img_bytes, "image/jpeg")},
            data={"width_cm": 0.05, "height_cm": 10, "dpi": 300},
        )
        assert response.status_code == 400

        # Width too large
        img_bytes = self.create_test_image()
        response = client.post(
            "/upscale",
            files={"image": ("test.jpg", img_bytes, "image/jpeg")},
            data={"width_cm": 500, "height_cm": 10, "dpi": 300},
        )
        assert response.status_code == 400

        # Height too small
        img_bytes = self.create_test_image()
        response = client.post(
            "/upscale",
            files={"image": ("test.jpg", img_bytes, "image/jpeg")},
            data={"width_cm": 10, "height_cm": 0.05, "dpi": 300},
        )
        assert response.status_code == 400

        # Height too large
        img_bytes = self.create_test_image()
        response = client.post(
            "/upscale",
            files={"image": ("test.jpg", img_bytes, "image/jpeg")},
            data={"width_cm": 10, "height_cm": 500, "dpi": 300},
        )
        assert response.status_code == 400

    def test_upscale_validates_dpi_range(self):
        """Test that DPI is validated."""
        img_bytes = self.create_test_image()

        # DPI too small
        response = client.post(
            "/upscale",
            files={"image": ("test.jpg", img_bytes, "image/jpeg")},
            data={"width_cm": 10, "height_cm": 10, "dpi": 5},
        )
        assert response.status_code == 400

        # DPI too large
        img_bytes = self.create_test_image()
        response = client.post(
            "/upscale",
            files={"image": ("test.jpg", img_bytes, "image/jpeg")},
            data={"width_cm": 10, "height_cm": 10, "dpi": 1500},
        )
        assert response.status_code == 400

    @pytest.mark.slow
    def test_upscale_success_with_cm_dpi(self):
        """Test successful image upscaling using cm/dpi with real panda image (slow test, requires model)."""
        # Load the real test image
        img_bytes = self.load_test_image()

        # 5cm x 5cm at 100 DPI = approximately 197x197 pixels
        response = client.post(
            "/upscale",
            files={"image": ("panda-low.jpeg", img_bytes, "image/jpeg")},
            data={"width_cm": 10, "height_cm": 10, "dpi": 150},
        )

        # This test requires the Real-ESRGAN model to be initialized
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        assert response.headers["content-type"] == "image/png"
        # Verify we got an image back
        output_img = Image.open(io.BytesIO(response.content))
        # 10cm x 10cm at 150 DPI = approximately 591x591 pixels
        # Should fit within this size (allowing aspect ratio preservation)
        assert output_img.size[0] <= 591
        assert output_img.size[1] <= 591
        assert output_img.size[0] > 100  # Should be upscaled

    def test_upscale_requires_either_pixels_or_cm_dpi(self):
        """Test that endpoint requires either pixel or cm/dpi parameters."""
        img_bytes = self.create_test_image()

        # No dimension parameters at all
        response = client.post(
            "/upscale",
            files={"image": ("test.jpg", img_bytes, "image/jpeg")},
            data={},
        )
        assert response.status_code == 400
