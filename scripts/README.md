# Scripts

This directory contains utility scripts for the Pandas Image Upscaler project.

## generate_logo_assets.py

Generates all logo assets (favicons, app icons, etc.) from a source logo image.

### Usage

```bash
# Generate from default source (assets/logo/panda-logo.png)
make generate-logo

# Or run directly with Python
python scripts/generate_logo_assets.py

# Generate from a custom source logo
python scripts/generate_logo_assets.py path/to/your/logo.png
```

### What it does

1. Takes a source logo image (recommended: 512x512 PNG with transparency)
2. Generates 14 different sizes for various devices and uses:
   - Favicons (16x16, 32x32)
   - Apple Touch Icon (180x180)
   - Android/PWA icons (48, 72, 96, 128, 144, 152, 192, 256, 512)
   - Multi-size favicon.ico file

### Output

All generated assets are saved to:
- `src/upscaler/static/logo/` - Web-accessible logo files

### Customizing the Logo

To use your own logo:

1. Create or modify `assets/logo/panda-logo.png` (512x512 recommended)
2. Run `make generate-logo`
3. All icon sizes will be automatically generated

### Requirements

- Python 3.12+
- Pillow (already in project dependencies)
