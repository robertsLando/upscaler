#!/usr/bin/env python3
"""
Simple test script to verify the upscaler API is working correctly.
"""
import requests
import io
from PIL import Image, ImageDraw


def create_test_image():
    """Create a simple test image"""
    img = Image.new('RGB', (100, 100), color='white')
    draw = ImageDraw.Draw(img)
    draw.rectangle([10, 10, 40, 40], fill='red')
    draw.rectangle([50, 50, 90, 90], fill='blue')
    draw.ellipse([30, 30, 70, 70], fill='green')
    return img


def test_health_endpoint():
    """Test the health check endpoint"""
    print("Testing health endpoint...")
    response = requests.get('http://localhost:8000/health')
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert data['status'] == 'healthy', f"Expected 'healthy', got {data['status']}"
    print("✓ Health check passed")


def test_upscale_endpoint():
    """Test the image upscaling endpoint"""
    print("\nTesting upscale endpoint...")
    
    # Create test image
    img = create_test_image()
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    # Send request
    files = {'image': ('test.jpg', img_bytes, 'image/jpeg')}
    data = {'target_width': 400, 'target_height': 400}
    
    print("Uploading test image (100x100) with target dimensions 400x400...")
    response = requests.post('http://localhost:8000/upscale', files=files, data=data)
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    assert response.headers['content-type'] == 'image/png', "Expected PNG response"
    
    # Verify the output image
    output_img = Image.open(io.BytesIO(response.content))
    print(f"✓ Received upscaled image: {output_img.size}")
    
    # Check dimensions (should be 400x400 or smaller maintaining aspect ratio)
    assert output_img.size[0] <= 400, f"Width {output_img.size[0]} exceeds target 400"
    assert output_img.size[1] <= 400, f"Height {output_img.size[1]} exceeds target 400"
    assert output_img.size[0] > 100 or output_img.size[1] > 100, "Image should be upscaled"
    
    print("✓ Upscale endpoint test passed")


def main():
    """Run all tests"""
    print("=" * 60)
    print("Image Upscaler API Test Suite")
    print("=" * 60)
    
    try:
        test_health_endpoint()
        test_upscale_endpoint()
        
        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        return 0
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1
    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Could not connect to server. Is it running on localhost:8000?")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        return 1


if __name__ == '__main__':
    exit(main())
