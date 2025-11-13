"""
Tests for the CLI module.
"""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from PIL import Image

from upscaler.cli import main, upscale_images_batch


class TestUpscaleImagesBatch:
    """Tests for the upscale_images_batch function."""

    def test_no_matching_files(self, tmp_path, caplog):
        """Test that function returns error when no files match pattern."""
        # Change to temp directory
        import os

        original_dir = os.getcwd()
        os.chdir(tmp_path)

        try:
            result = upscale_images_batch("*.jpg", target_width=800, target_height=600)
            assert result == 1

            assert "No files found" in caplog.text
        finally:
            os.chdir(original_dir)

    def test_invalid_image_file(self, tmp_path, caplog):
        """Test handling of invalid image files."""
        import os

        original_dir = os.getcwd()
        os.chdir(tmp_path)

        try:
            # Create a non-image file with image extension
            invalid_file = tmp_path / "test.jpg"
            invalid_file.write_text("not an image")

            result = upscale_images_batch("*.jpg", target_width=800, target_height=600)
            # Should return 1 as no images were successfully processed
            assert result == 1

            assert "Failed to process" in caplog.text
        finally:
            os.chdir(original_dir)

    def test_successful_single_image_processing(self, tmp_path):
        """Test successful processing of a single image."""
        import os

        original_dir = os.getcwd()
        os.chdir(tmp_path)

        try:
            # Create a simple test image
            img = Image.new("RGB", (100, 100), color="red")
            test_file = tmp_path / "test.jpg"
            img.save(test_file)

            result = upscale_images_batch("test.jpg", target_width=400, target_height=400)
            assert result == 0

            # Check output file exists
            output_file = tmp_path / "test_upscaled.jpg"
            assert output_file.exists()

            # Verify output image
            output_img = Image.open(output_file)
            assert output_img.size == (400, 400)
        finally:
            os.chdir(original_dir)

    def test_glob_pattern_multiple_files(self, tmp_path):
        """Test processing multiple files with glob pattern."""
        import os

        original_dir = os.getcwd()
        os.chdir(tmp_path)

        try:
            # Create multiple test images
            for i in range(3):
                img = Image.new("RGB", (50, 50), color="blue")
                img.save(tmp_path / f"test{i}.png")

            result = upscale_images_batch("*.png", target_width=200, target_height=200)
            assert result == 0

            # Check all output files exist
            for i in range(3):
                output_file = tmp_path / f"test{i}_upscaled.png"
                assert output_file.exists()
        finally:
            os.chdir(original_dir)

    def test_subdirectory_glob_pattern(self, tmp_path):
        """Test glob pattern with subdirectory."""
        import os

        original_dir = os.getcwd()
        os.chdir(tmp_path)

        try:
            # Create subdirectory with images
            subdir = tmp_path / "images"
            subdir.mkdir()

            img = Image.new("RGB", (100, 100), color="green")
            img.save(subdir / "test.jpg")

            result = upscale_images_batch("images/*.jpg", target_width=400, target_height=400)
            assert result == 0

            # Check output file exists in subdirectory
            output_file = subdir / "test_upscaled.jpg"
            assert output_file.exists()
        finally:
            os.chdir(original_dir)

    def test_preserves_aspect_ratio(self, tmp_path):
        """Test that aspect ratio is preserved during upscaling."""
        import os

        original_dir = os.getcwd()
        os.chdir(tmp_path)

        try:
            # Create a wide image (2:1 aspect ratio)
            img = Image.new("RGB", (200, 100), color="purple")
            test_file = tmp_path / "wide.jpg"
            img.save(test_file)

            result = upscale_images_batch("wide.jpg", target_width=800, target_height=600)
            assert result == 0

            # Check output preserves aspect ratio
            output_file = tmp_path / "wide_upscaled.jpg"
            output_img = Image.open(output_file)

            # Should be limited by width: 800x400
            assert output_img.size == (800, 400)
        finally:
            os.chdir(original_dir)


class TestMainCLI:
    """Tests for the main CLI function."""

    def test_help_flag(self):
        """Test that --help flag works."""
        with patch("sys.argv", ["upscaler-cli", "--help"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

    def test_invalid_width(self, caplog):
        """Test validation of width parameter."""
        with patch("sys.argv", ["upscaler-cli", "*.jpg", "-w", "20000", "--height", "600"]):
            result = main()
            assert result == 1

            assert "Width must be between" in caplog.text

    def test_invalid_height(self, caplog):
        """Test validation of height parameter."""
        with patch("sys.argv", ["upscaler-cli", "*.jpg", "-w", "800", "--height", "0"]):
            result = main()
            assert result == 1

            assert "Height must be between" in caplog.text

    def test_missing_arguments(self):
        """Test that missing arguments cause error."""
        with patch("sys.argv", ["upscaler-cli", "*.jpg"]):
            result = main()
            assert result == 1

    def test_verbose_flag(self, tmp_path):
        """Test that verbose flag enables debug logging."""
        import os

        original_dir = os.getcwd()
        os.chdir(tmp_path)

        try:
            # Create a test image
            img = Image.new("RGB", (100, 100), color="red")
            test_file = tmp_path / "test.jpg"
            img.save(test_file)

            with patch(
                "sys.argv", ["upscaler-cli", "-v", "test.jpg", "-w", "400", "--height", "400"]
            ):
                result = main()
                assert result == 0
        finally:
            os.chdir(original_dir)

    def test_cm_dpi_mode(self, tmp_path):
        """Test processing with cm and DPI mode."""
        import os

        original_dir = os.getcwd()
        os.chdir(tmp_path)

        try:
            # Create a test image
            img = Image.new("RGB", (100, 100), color="blue")
            test_file = tmp_path / "test.jpg"
            img.save(test_file)

            result = upscale_images_batch("test.jpg", width_cm=10.0, height_cm=10.0, dpi=100)
            assert result == 0

            # Check output file exists
            output_file = tmp_path / "test_upscaled.jpg"
            assert output_file.exists()
        finally:
            os.chdir(original_dir)

    def test_cm_dpi_mode_cli(self, tmp_path):
        """Test CLI with cm and DPI arguments."""
        import os

        original_dir = os.getcwd()
        os.chdir(tmp_path)

        try:
            # Create a test image
            img = Image.new("RGB", (100, 100), color="green")
            test_file = tmp_path / "test.jpg"
            img.save(test_file)

            with patch(
                "sys.argv",
                [
                    "upscaler-cli",
                    "test.jpg",
                    "--width-cm",
                    "10",
                    "--height-cm",
                    "10",
                    "--dpi",
                    "100",
                ],
            ):
                result = main()
                assert result == 0

            # Check output file exists
            output_file = tmp_path / "test_upscaled.jpg"
            assert output_file.exists()
        finally:
            os.chdir(original_dir)

    def test_mixed_mode_error(self, caplog):
        """Test that mixing pixel and cm modes produces error."""
        with patch(
            "sys.argv",
            [
                "upscaler-cli",
                "*.jpg",
                "-w",
                "800",
                "--height",
                "600",
                "--width-cm",
                "10",
            ],
        ):
            result = main()
            assert result == 1
            assert "Cannot mix" in caplog.text
