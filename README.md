# upscaler

AI-powered image upscaler using Real-ESRGAN with a web API and UI.

## Quick Start

```bash
# Install uv
pip install uv

# Clone and setup
git clone https://github.com/robertsLando/upscaler.git
cd upscaler
uv sync

# Run the server
uv run python main.py
```

Then open http://localhost:8000 in your browser! 🚀

## Features

- 🚀 Fast image upscaling using Real-ESRGAN
- 🎨 Web UI for easy image upload and download
- 📐 Aspect ratio preservation
- 🔧 RESTful API for programmatic access
- 📦 Managed with uv for fast dependency resolution

## Requirements

- Python 3.12+
- uv package manager

## Installation

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
uv sync
```

## Usage

### Starting the Server

Run the server using uv:

```bash
uv run python main.py
```

Or using uvicorn directly:

```bash
uv run uvicorn main:app --host 0.0.0.0 --port 8000
```

The server will start at `http://localhost:8000`

### Web UI

1. Open your browser and navigate to `http://localhost:8000`
2. Upload an image
3. Set target width and height (in pixels)
4. Click "Upscale Image"
5. Preview and download the upscaled result

### API Usage

**Endpoint:** `POST /upscale`

**Parameters:**
- `image`: Image file (multipart/form-data)
- `target_width`: Target width in pixels (1-4096)
- `target_height`: Target height in pixels (1-4096)

**Example using curl:**

```bash
curl -X POST "http://localhost:8000/upscale" \
  -F "image=@input.jpg" \
  -F "target_width=1920" \
  -F "target_height=1080" \
  --output upscaled.png
```

**Example using Python:**

```python
import requests

with open('input.jpg', 'rb') as f:
    files = {'image': f}
    data = {'target_width': 1920, 'target_height': 1080}
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

## Technical Details

- **Framework**: FastAPI for the web API
- **AI Model**: Real-ESRGAN (x4plus) for high-quality upscaling
- **Image Processing**: Pillow (PIL) for image manipulation
- **Package Manager**: uv for fast, reliable dependency management

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

