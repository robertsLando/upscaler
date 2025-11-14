#!/usr/bin/env python3
"""
Generate logo assets in multiple sizes from the source logo.
Usage: python scripts/generate_logo_assets.py [source_logo_path]
"""
import sys
from pathlib import Path
from PIL import Image


def create_logo_from_source(source_path: str, size: int) -> Image.Image:
    """Load and resize source logo to target size."""
    img = Image.open(source_path)
    
    # Ensure RGBA mode for transparency
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # Resize with high-quality resampling
    resized = img.resize((size, size), Image.Resampling.LANCZOS)
    
    return resized


def generate_assets(source_logo: str = "assets/logo/panda-logo.png"):
    """Generate all logo assets from source logo."""
    source_path = Path(source_logo)
    
    if not source_path.exists():
        print(f"Error: Source logo not found at {source_logo}")
        print("Please ensure the source logo exists at assets/logo/panda-logo.png")
        sys.exit(1)
    
    print(f"Generating logo assets from: {source_logo}")
    
    # Ensure directories exist
    assets_logo_dir = Path("assets/logo")
    static_logo_dir = Path("src/upscaler/static/logo")
    
    assets_logo_dir.mkdir(parents=True, exist_ok=True)
    static_logo_dir.mkdir(parents=True, exist_ok=True)
    
    # Define all sizes needed
    sizes = [
        (512, 'panda-logo-512.png', static_logo_dir),
        (256, 'panda-logo-256.png', static_logo_dir),
        (192, 'panda-logo-192.png', static_logo_dir),
        (180, 'apple-touch-icon.png', static_logo_dir),
        (152, 'panda-logo-152.png', static_logo_dir),
        (144, 'panda-logo-144.png', static_logo_dir),
        (128, 'panda-logo-128.png', static_logo_dir),
        (96, 'panda-logo-96.png', static_logo_dir),
        (72, 'panda-logo-72.png', static_logo_dir),
        (48, 'panda-logo-48.png', static_logo_dir),
        (32, 'favicon-32x32.png', static_logo_dir),
        (16, 'favicon-16x16.png', static_logo_dir),
        (512, 'panda-logo.png', static_logo_dir),  # Main logo in static
    ]
    
    # Generate all sizes
    for size, filename, output_dir in sizes:
        resized = create_logo_from_source(source_logo, size)
        output_path = output_dir / filename
        resized.save(output_path)
        print(f"Created: {output_path} ({size}x{size})")
    
    # Create favicon.ico (multi-size ICO file)
    favicon_sizes = [16, 32, 48]
    favicon_images = [create_logo_from_source(source_logo, s) for s in favicon_sizes]
    favicon_path = static_logo_dir / 'favicon.ico'
    favicon_images[0].save(
        favicon_path,
        format='ICO',
        sizes=[(s, s) for s in favicon_sizes]
    )
    print(f"Created: {favicon_path} (16x16, 32x32, 48x48)")
    
    print("\n✅ All logo assets generated successfully!")
    print(f"   Source: {source_logo}")
    print(f"   Output: {static_logo_dir}/")


if __name__ == "__main__":
    source_logo = sys.argv[1] if len(sys.argv) > 1 else "assets/logo/panda-logo.png"
    generate_assets(source_logo)
