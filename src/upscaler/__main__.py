#!/usr/bin/env python
"""
Entry point for the image upscaler application.
"""
import uvicorn

from upscaler import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
