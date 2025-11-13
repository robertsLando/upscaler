"""
Command-line interface for the image upscaler.
"""

import argparse
import logging
import sys
from pathlib import Path

from PIL import Image

from .upscaler import cm_to_pixels
from .utils import upscale_image

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def upscale_images_batch(
    glob_pattern: str,
    target_width: int = None,
    target_height: int = None,
    width_cm: float = None,
    height_cm: float = None,
    dpi: int = None,
):
    """
    Upscale all images matching the glob pattern to target dimensions.

    You can specify dimensions in two ways:
    1. Directly in pixels using target_width and target_height
    2. In centimeters and DPI using width_cm, height_cm, and dpi

    Args:
        glob_pattern: Glob pattern to match image files (e.g., "*.jpg", "images/*.png")
        target_width: Target width in pixels (1-10000)
        target_height: Target height in pixels (1-10000)
        width_cm: Target width in centimeters (0.1-400)
        height_cm: Target height in centimeters (0.1-400)
        dpi: Dots per inch (10-1200)
    """
    # Determine which input method to use and convert if needed
    if width_cm is not None or height_cm is not None or dpi is not None:
        # Using cm/dpi mode
        if width_cm is None or height_cm is None or dpi is None:
            logger.error(
                "When using cm/dpi mode, all three parameters (width_cm, height_cm, dpi) are required"
            )
            return 1

        # Convert cm to pixels
        target_width, target_height = cm_to_pixels(width_cm, height_cm, dpi)
        logger.info(
            f"Converted {width_cm}cm x {height_cm}cm @ {dpi}dpi to {target_width}px x {target_height}px"
        )

    # Find all matching files
    current_dir = Path.cwd()
    matching_files = list(current_dir.glob(glob_pattern))

    if not matching_files:
        logger.error(f"No files found matching pattern: {glob_pattern}")
        return 1

    logger.info(f"Found {len(matching_files)} file(s) to process")

    # Process each file
    success_count = 0
    for file_path in matching_files:
        try:
            logger.info(f"Processing: {file_path.name}")

            # Load image
            img = Image.open(file_path)

            # Upscale the image using shared utility function
            final_img = upscale_image(img, target_width, target_height)

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
  # Upscale all JPG files in current directory to 1920x1080 pixels
  upscaler-cli "*.jpg" -w 1920 --height 1080

  # Upscale all PNG files in images/ directory using cm and DPI
  upscaler-cli "images/*.png" --width-cm 20 --height-cm 15 --dpi 300

  # Upscale a specific image with verbose logging
  upscaler-cli "photo.jpg" -w 3840 --height 2160 -v
        """,
    )

    parser.add_argument(
        "glob_pattern",
        type=str,
        help="Glob pattern to match image files (e.g., '*.jpg', 'images/*.png')",
    )

    # Pixel-based dimensions
    parser.add_argument(
        "-w",
        "--width",
        type=int,
        help="Target width in pixels (1-10000)",
    )

    parser.add_argument(
        "--height",
        type=int,
        help="Target height in pixels (1-10000)",
    )

    # Centimeter-based dimensions
    parser.add_argument(
        "--width-cm",
        type=float,
        help="Target width in centimeters (0.1-400)",
    )

    parser.add_argument(
        "--height-cm",
        type=float,
        help="Target height in centimeters (0.1-400)",
    )

    parser.add_argument(
        "--dpi",
        type=int,
        help="Dots per inch (10-1200) - required when using --width-cm/--height-cm",
    )

    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Determine which input method to use
    using_cm = args.width_cm is not None or args.height_cm is not None or args.dpi is not None
    using_pixels = args.width is not None or args.height is not None

    if not using_cm and not using_pixels:
        logger.error(
            "Either provide --width and --height (in pixels) or --width-cm, --height-cm, and --dpi"
        )
        return 1

    if using_cm and using_pixels:
        logger.error("Cannot mix pixel-based and cm-based dimensions. Choose one mode.")
        return 1

    # Validate based on mode
    if using_cm:
        if args.width_cm is None or args.height_cm is None or args.dpi is None:
            logger.error(
                "When using cm/dpi mode, all three parameters (--width-cm, --height-cm, --dpi) are required"
            )
            return 1

        # Validate cm dimensions
        if args.width_cm < 0.1 or args.width_cm > 400:
            logger.error("Width must be between 0.1 and 400 centimeters")
            return 1

        if args.height_cm < 0.1 or args.height_cm > 400:
            logger.error("Height must be between 0.1 and 400 centimeters")
            return 1

        # Validate DPI
        if args.dpi < 10 or args.dpi > 1200:
            logger.error("DPI must be between 10 and 1200")
            return 1

        # Run batch upscaling with cm/dpi
        return upscale_images_batch(
            args.glob_pattern,
            width_cm=args.width_cm,
            height_cm=args.height_cm,
            dpi=args.dpi,
        )
    else:
        # Validate pixel dimensions
        if args.width is None or args.height is None:
            logger.error("Both --width and --height are required in pixel mode")
            return 1

        if not (1 <= args.width <= 10000):
            logger.error("Width must be between 1 and 10000 pixels")
            return 1

        if not (1 <= args.height <= 10000):
            logger.error("Height must be between 1 and 10000 pixels")
            return 1

        # Run batch upscaling with pixels
        return upscale_images_batch(
            args.glob_pattern,
            target_width=args.width,
            target_height=args.height,
        )


if __name__ == "__main__":
    sys.exit(main())
