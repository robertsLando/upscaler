"""
Shared test fixtures and configuration for pytest.
"""

import io
from pathlib import Path

import pytest
from PIL import Image


@pytest.fixture
def test_image_path():
    """Fixture that provides the path to the panda test image."""
    return Path(__file__).parent / "assets" / "panda-low.jpeg"


@pytest.fixture
def panda_test_image(test_image_path):
    """Fixture that loads the panda test image as a BytesIO object for API tests."""
    with open(test_image_path, "rb") as f:
        return io.BytesIO(f.read())


@pytest.fixture
def panda_pil_image(test_image_path):
    """Fixture that loads the panda test image as a PIL Image object."""
    return Image.open(test_image_path)
