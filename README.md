# upscaler

[![CI](https://github.com/robertsLando/upscaler/actions/workflows/ci.yml/badge.svg)](https://github.com/robertsLando/upscaler/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/robertsLando/upscaler/branch/main/graph/badge.svg)](https://codecov.io/gh/robertsLando/upscaler)
[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

AI-powered image upscaler using Real-ESRGAN with a web API and UI.

## Quick Start

### With Docker (Easiest)

```bash
# Clone the repository
git clone https://github.com/robertsLando/upscaler.git
cd upscaler

# Start with docker-compose
docker-compose up
```

Then open http://localhost:8000 in your browser! 🚀

### Without Docker

```bash
# Install uv
pip install uv

# Clone and setup
git clone https://github.com/robertsLando/upscaler.git
cd upscaler
uv sync

# Run the server
make run
# Or: uv run python -m upscaler
```

Then open http://localhost:8000 in your browser! 🚀

## Features

- 🚀 Fast image upscaling using Real-ESRGAN
- 🐳 Docker support for easy deployment
- 💻 Command-line interface for batch processing with glob patterns
- 🎨 Web UI for easy image upload and download
- 📐 Aspect ratio preservation
- 📏 Dual dimension input modes:
  - **Pixels**: Direct pixel dimensions (1-10000 px)
  - **Centimeters + DPI**: Physical dimensions with resolution (0.1-400 cm, 10-1200 DPI)
- 🔧 RESTful API for programmatic access
- 📦 Managed with uv for fast dependency resolution
- 🧪 Comprehensive test suite
- 🎯 Linting and formatting with ruff and black

## Requirements

- Python 3.12+
- uv package manager

**OR**

- Docker (for containerized usage)

## Installation

### Option 1: Using Docker (Recommended)

Docker provides the easiest way to run the upscaler without installing dependencies.

#### Using Docker Compose

1. Clone the repository:
```bash
git clone https://github.com/robertsLando/upscaler.git
cd upscaler
```

2. Start the webserver:
```bash
docker-compose up
```

The server will be available at `http://localhost:8000`

3. Using the CLI:
```bash
# Create an images directory and place your images there
mkdir -p images
cp your-image.jpg images/

# Run the CLI to upscale images
docker-compose run --rm upscaler upscaler-cli "/images/*.jpg" -w 1920 --height 1080

# Upscaled images will be saved in the images/ directory
```

#### Using Docker directly

1. Pull the image:
```bash
docker pull ghcr.io/robertslando/upscaler:latest
# Or from Docker Hub:
# docker pull <username>/upscaler:latest
```

2. Run the webserver:
```bash
docker run -p 8000:8000 ghcr.io/robertslando/upscaler:latest
```

3. Use the CLI:
```bash
# Mount a local directory with images
docker run -v $(pwd)/images:/images ghcr.io/robertslando/upscaler:latest \
  upscaler-cli "/images/*.jpg" -w 1920 --height 1080
```

4. Build locally:
```bash
docker build -t upscaler .
docker run -p 8000:8000 upscaler
```

### Option 2: Local Installation

1. Install uv if you haven't already:
```bash
pip install uv
```

2. Clone the repository:
```bash
git clone https://github.com/robertsLando/upscaler.git
cd upscaler
```

3. Install dependencies using uv:
```bash
make install
# Or: uv sync
```

## Usage

### CLI Usage

The CLI allows batch processing of images using glob patterns with support for both pixel-based and physical dimensions (cm/DPI).

**Command formats:**

```bash
# Using pixels
upscaler-cli <glob_pattern> -w <width> --height <height>

# Using centimeters and DPI
upscaler-cli <glob_pattern> --width-cm <width> --height-cm <height> --dpi <dpi>
```

**Examples:**

```bash
# Upscale all JPG files in current directory to 1920x1080 pixels
upscaler-cli "*.jpg" -w 1920 --height 1080

# Upscale all PNG files using physical dimensions (20x15 cm at 300 DPI)
upscaler-cli "images/*.png" --width-cm 20 --height-cm 15 --dpi 300

# Upscale a specific image with verbose logging
upscaler-cli -v "photo.jpg" -w 3840 --height 2160
```

**Options:**
- `-w, --width`: Target width in pixels (1-10000)
- `--height`: Target height in pixels (1-10000)
- `--width-cm`: Target width in centimeters (0.1-400)
- `--height-cm`: Target height in centimeters (0.1-400)
- `--dpi`: Dots per inch (10-1200) - required when using cm dimensions
- `-v, --verbose`: Enable verbose logging
- `-h, --help`: Show help message

Upscaled images are saved with `_upscaled` suffix in the same directory as the original.

### Starting the Server

Run the server using Make:

```bash
make run
```

Or using uv directly:

```bash
uv run python -m upscaler
```

The server will start at `http://localhost:8000`

### Development

```bash
# Run tests
make test

# Run linter
make lint

# Format code
make format

# Run all tests including slow ones
uv run pytest tests/ -v

# Run with coverage
make test-cov
```

### Web UI

1. Open your browser and navigate to `http://localhost:8000`
2. Upload an image
3. Choose your preferred dimension mode:
   - **Pixels (px)**: Set target width and height directly in pixels
   - **Centimeters + DPI**: Set dimensions in centimeters and specify DPI resolution
4. Click "Upscale Image"
5. Preview and download the upscaled result

### API Usage

**Endpoint:** `POST /upscale`

**Parameters (Pixel Mode):**
- `image`: Image file (multipart/form-data)
- `target_width`: Target width in pixels (1-10000)
- `target_height`: Target height in pixels (1-10000)

**Parameters (CM/DPI Mode):**
- `image`: Image file (multipart/form-data)
- `width_cm`: Target width in centimeters (0.1-400)
- `height_cm`: Target height in centimeters (0.1-400)
- `dpi`: Dots per inch resolution (10-1200)

**Example using curl (pixels):**

```bash
curl -X POST "http://localhost:8000/upscale" \
  -F "image=@input.jpg" \
  -F "target_width=1920" \
  -F "target_height=1080" \
  --output upscaled.png
```

**Example using curl (centimeters + DPI):**

```bash
# A4 size at 300 DPI
curl -X POST "http://localhost:8000/upscale" \
  -F "image=@input.jpg" \
  -F "width_cm=21" \
  -F "height_cm=29.7" \
  -F "dpi=300" \
  --output upscaled.png
```

**Example using Python:**

```python
import requests

# Using pixels
with open('input.jpg', 'rb') as f:
    files = {'image': f}
    data = {'target_width': 1920, 'target_height': 1080}
    response = requests.post('http://localhost:8000/upscale', files=files, data=data)
    
    with open('upscaled.png', 'wb') as out:
        out.write(response.content)

# Using centimeters and DPI
with open('input.jpg', 'rb') as f:
    files = {'image': f}
    data = {'width_cm': 10, 'height_cm': 15, 'dpi': 300}
    response = requests.post('http://localhost:8000/upscale', files=files, data=data)
    
    with open('upscaled.png', 'wb') as out:
        out.write(response.content)
```

### Health Check

```bash
curl http://localhost:8000/health
```

## How It Works

1. **Upload**: Users upload an image and specify target dimensions
2. **Upscale**: The image is upscaled 4x using Real-ESRGAN AI model
3. **Resize**: The upscaled image is resized to fit target dimensions while preserving aspect ratio
4. **Download**: The final image is returned as a PNG file

## Project Structure

```
upscaler/
├── src/
│   └── upscaler/
│       ├── __init__.py         # Package initialization
│       ├── __main__.py         # Entry point for running the app
│       ├── app.py              # FastAPI application and routes
│       ├── upscaler.py         # Core upscaling logic
│       └── templates/
│           └── index.html      # Web UI template
├── tests/
│   ├── __init__.py
│   ├── test_api.py             # API integration tests
│   └── test_upscaler.py        # Unit tests
├── Makefile                    # Common development commands
├── pyproject.toml              # Project configuration and dependencies
├── uv.lock                     # Locked dependency versions
└── README.md                   # This file
```

## Technical Details

- **Framework**: FastAPI for the web API
- **AI Model**: Real-ESRGAN (x4plus) for high-quality upscaling
- **Image Processing**: Pillow (PIL) for image manipulation
- **Package Manager**: uv for fast, reliable dependency management
- **Testing**: pytest with comprehensive unit and integration tests
- **Linting**: ruff for fast Python linting
- **Formatting**: black for code formatting

## Model Information

The application uses the RealESRGAN_x4plus model which:
- Upscales images by 4x
- Works well for general photos and artwork
- Downloads automatically on first use (~64MB)
- Runs on CPU (GPU support can be enabled by modifying the code)

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

