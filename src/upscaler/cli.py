"""
Command-line interface for the image upscaler.
"""

import argparse
import logging
import sys
from pathlib import Path

import numpy as np
from PIL import Image

from .upscaler import get_upsampler, resize_to_target

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def upscale_images_batch(glob_pattern: str, target_width: int, target_height: int):
    """
    Upscale all images matching the glob pattern to target dimensions.

    Args:
        glob_pattern: Glob pattern to match image files (e.g., "*.jpg", "images/*.png")
        target_width: Target width in pixels (1-10000)
        target_height: Target height in pixels (1-10000)
    """
    # Find all matching files
    current_dir = Path.cwd()
    matching_files = list(current_dir.glob(glob_pattern))

    if not matching_files:
        logger.error(f"No files found matching pattern: {glob_pattern}")
        return 1

    logger.info(f"Found {len(matching_files)} file(s) to process")

    # Get upsampler (lazy loaded)
    upsampler = get_upsampler()

    # Process each file
    success_count = 0
    for file_path in matching_files:
        try:
            logger.info(f"Processing: {file_path.name}")

            # Load image
            img = Image.open(file_path)

            # Convert to RGB if necessary
            if img.mode != "RGB":
                img = img.convert("RGB")

            logger.info(f"  Original size: {img.size}")

            # Convert PIL Image to numpy array
            img_np = np.array(img)

            # Upscale with Real-ESRGAN
            output, _ = upsampler.enhance(img_np, outscale=4)
            logger.info(f"  Upscaled to: {output.shape[:2][::-1]}")

            # Convert back to PIL Image
            upscaled_img = Image.fromarray(output)

            # Resize to target dimensions while preserving aspect ratio
            final_img = resize_to_target(upscaled_img, target_width, target_height)
            logger.info(f"  Final size: {final_img.size}")

            # Generate output filename
            output_path = file_path.parent / f"{file_path.stem}_upscaled{file_path.suffix}"
            if output_path.suffix.lower() not in [".png", ".jpg", ".jpeg"]:
                output_path = output_path.with_suffix(".png")

            # Save the result
            final_img.save(output_path, format="PNG")
            logger.info(f"  Saved to: {output_path}")

            success_count += 1

        except Exception as e:
            logger.error(f"  Failed to process {file_path.name}: {str(e)}")
            continue

    logger.info(f"Successfully processed {success_count}/{len(matching_files)} image(s)")
    return 0 if success_count > 0 else 1


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Upscale images using Real-ESRGAN AI model",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Upscale all JPG files in current directory to 1920x1080
  upscaler-cli "*.jpg" 1920 1080

  # Upscale all PNG files in images/ directory to 2560x1440
  upscaler-cli "images/*.png" 2560 1440

  # Upscale a specific image
  upscaler-cli "photo.jpg" 3840 2160
        """,
    )

    parser.add_argument(
        "glob_pattern",
        type=str,
        help="Glob pattern to match image files (e.g., '*.jpg', 'images/*.png')",
    )

    parser.add_argument("target_width", type=int, help="Target width in pixels (1-10000)")

    parser.add_argument("target_height", type=int, help="Target height in pixels (1-10000)")

    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Validate dimensions
    if not (1 <= args.target_width <= 10000):
        logger.error("Width must be between 1 and 10000 pixels")
        return 1

    if not (1 <= args.target_height <= 10000):
        logger.error("Height must be between 1 and 10000 pixels")
        return 1

    # Run the batch upscaling
    return upscale_images_batch(args.glob_pattern, args.target_width, args.target_height)


if __name__ == "__main__":
    sys.exit(main())
