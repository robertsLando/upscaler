import os
import io
import sys
import tempfile
from pathlib import Path
from typing import Optional
import logging

# Patch for torchvision compatibility with basicsr
# basicsr expects torchvision.transforms.functional_tensor which was renamed in newer versions
import torchvision.transforms.functional as F
sys.modules['torchvision.transforms.functional_tensor'] = F

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Image Upscaler API", description="Upscale images using Real-ESRGAN")

# Initialize Real-ESRGAN upsampler lazily to avoid startup delays
_upsampler = None


def get_upsampler():
    """Lazy initialization of Real-ESRGAN model"""
    global _upsampler
    if _upsampler is None:
        try:
            from realesrgan import RealESRGANer
            from basicsr.archs.rrdbnet_arch import RRDBNet
            
            logger.info("Initializing Real-ESRGAN model...")
            
            # Use RealESRGAN_x4plus model
            model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4)
            
            # Initialize upsampler - it will download the model automatically
            _upsampler = RealESRGANer(
                scale=4,
                model_path='https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth',
                model=model,
                tile=0,
                tile_pad=10,
                pre_pad=0,
                half=False,  # Use FP32 for CPU compatibility
                gpu_id=None  # Use CPU
            )
            logger.info("Real-ESRGAN model initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Real-ESRGAN: {e}")
            raise
    return _upsampler


def resize_to_target(image: Image.Image, target_width: int, target_height: int) -> Image.Image:
    """
    Resize image to target dimensions while preserving aspect ratio.
    The image will fit within the target dimensions.
    """
    original_width, original_height = image.size
    
    # Calculate aspect ratios
    target_ratio = target_width / target_height
    original_ratio = original_width / original_height
    
    # Determine new size maintaining aspect ratio
    if original_ratio > target_ratio:
        # Width is the limiting factor
        new_width = target_width
        new_height = int(target_width / original_ratio)
    else:
        # Height is the limiting factor
        new_height = target_height
        new_width = int(target_height * original_ratio)
    
    return image.resize((new_width, new_height), Image.LANCZOS)


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the HTML UI"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Image Upscaler</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                background-color: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #333;
                text-align: center;
            }
            .form-group {
                margin-bottom: 20px;
            }
            label {
                display: block;
                margin-bottom: 5px;
                font-weight: bold;
                color: #555;
            }
            input[type="file"],
            input[type="number"] {
                width: 100%;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
                box-sizing: border-box;
            }
            .dimension-inputs {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 15px;
            }
            button {
                width: 100%;
                padding: 12px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
                font-weight: bold;
            }
            button:hover {
                background-color: #45a049;
            }
            button:disabled {
                background-color: #ccc;
                cursor: not-allowed;
            }
            #status {
                margin-top: 20px;
                padding: 10px;
                border-radius: 5px;
                display: none;
            }
            .success {
                background-color: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
            }
            .error {
                background-color: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
            }
            .info {
                background-color: #d1ecf1;
                color: #0c5460;
                border: 1px solid #bee5eb;
            }
            .preview {
                margin-top: 20px;
                text-align: center;
            }
            .preview img {
                max-width: 100%;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🖼️ Image Upscaler</h1>
            <p style="text-align: center; color: #666;">Upload an image and specify target dimensions for AI-powered upscaling</p>
            
            <form id="uploadForm">
                <div class="form-group">
                    <label for="image">Select Image:</label>
                    <input type="file" id="image" name="image" accept="image/*" required>
                </div>
                
                <div class="dimension-inputs">
                    <div class="form-group">
                        <label for="width">Target Width (px):</label>
                        <input type="number" id="width" name="width" min="1" max="4096" value="1024" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="height">Target Height (px):</label>
                        <input type="number" id="height" name="height" min="1" max="4096" value="1024" required>
                    </div>
                </div>
                
                <button type="submit" id="submitBtn">Upscale Image</button>
            </form>
            
            <div id="status"></div>
            
            <div class="preview" id="preview" style="display: none;">
                <h3>Preview:</h3>
                <img id="previewImg" src="" alt="Upscaled image preview">
                <br><br>
                <button id="downloadBtn" onclick="downloadImage()">Download Image</button>
            </div>
        </div>
        
        <script>
            let uploadedImageData = null;
            
            document.getElementById('uploadForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const formData = new FormData();
                const imageFile = document.getElementById('image').files[0];
                const width = document.getElementById('width').value;
                const height = document.getElementById('height').value;
                
                formData.append('image', imageFile);
                formData.append('target_width', width);
                formData.append('target_height', height);
                
                const statusDiv = document.getElementById('status');
                const submitBtn = document.getElementById('submitBtn');
                const preview = document.getElementById('preview');
                
                statusDiv.style.display = 'block';
                statusDiv.className = 'info';
                statusDiv.textContent = 'Upscaling image... This may take a moment.';
                submitBtn.disabled = true;
                preview.style.display = 'none';
                
                try {
                    const response = await fetch('/upscale', {
                        method: 'POST',
                        body: formData
                    });
                    
                    if (!response.ok) {
                        const error = await response.json();
                        throw new Error(error.detail || 'Failed to upscale image');
                    }
                    
                    const blob = await response.blob();
                    uploadedImageData = blob;
                    const imageUrl = URL.createObjectURL(blob);
                    
                    document.getElementById('previewImg').src = imageUrl;
                    preview.style.display = 'block';
                    
                    statusDiv.className = 'success';
                    statusDiv.textContent = '✓ Image upscaled successfully!';
                } catch (error) {
                    statusDiv.className = 'error';
                    statusDiv.textContent = '✗ Error: ' + error.message;
                } finally {
                    submitBtn.disabled = false;
                }
            });
            
            function downloadImage() {
                if (uploadedImageData) {
                    const url = URL.createObjectURL(uploadedImageData);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'upscaled_image.png';
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    URL.revokeObjectURL(url);
                }
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.post("/upscale")
async def upscale_image(
    image: UploadFile = File(...),
    target_width: int = Form(...),
    target_height: int = Form(...)
):
    """
    Upscale an image to target dimensions using Real-ESRGAN.
    The aspect ratio is preserved.
    """
    # Validate inputs
    if target_width < 1 or target_width > 4096:
        raise HTTPException(status_code=400, detail="Width must be between 1 and 4096 pixels")
    if target_height < 1 or target_height > 4096:
        raise HTTPException(status_code=400, detail="Height must be between 1 and 4096 pixels")
    
    # Check file type
    if not image.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        # Read the uploaded image
        contents = await image.read()
        img = Image.open(io.BytesIO(contents))
        
        # Convert to RGB if necessary
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        logger.info(f"Original image size: {img.size}")
        
        # Get upsampler
        upsampler = get_upsampler()
        
        # Convert PIL Image to numpy array
        img_np = np.array(img)
        
        # Upscale with Real-ESRGAN
        logger.info("Starting upscaling process...")
        output, _ = upsampler.enhance(img_np, outscale=4)
        logger.info(f"Upscaled to: {output.shape}")
        
        # Convert back to PIL Image
        upscaled_img = Image.fromarray(output)
        
        # Resize to target dimensions while preserving aspect ratio
        final_img = resize_to_target(upscaled_img, target_width, target_height)
        logger.info(f"Final image size: {final_img.size}")
        
        # Save to bytes buffer
        img_byte_arr = io.BytesIO()
        final_img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        return StreamingResponse(
            img_byte_arr,
            media_type="image/png",
            headers={
                "Content-Disposition": f"attachment; filename=upscaled_{image.filename}"
            }
        )
        
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Image upscaler API is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
