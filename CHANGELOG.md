## 1.2.0 (2025-11-14)

### Feat

- **ui**: drag-and-drop upload with image previews, metadata display, panda logo branding, and asset generation (#13)

### Fix

- free disk space before multi-platform Docker build (#11)
- update Docker image tag handling to include branch references and SHA
- update Docker image tag input description and default value

## 1.1.0 (2025-11-13)

### Feat

- add real test image (panda-low.jpeg) and update tests to use it for upscaling and resizing (#8)
- add Docker support with multi-platform builds and automated publishing (#7)
- add CLI entrypoint for batch image upscaling with glob patterns and cm/DPI support (#3)
- add centimeter/DPI dimension input mode (#5)

### Fix

- correct coverage report configuration in CI and Makefile
- simplify Makefile commands by removing unnecessary PYTHONPATH assignments
- correct authors section formatting in pyproject.toml

## 1.0.0 (2025-11-12)

### Feat

- add release script for versioning and changelog management
- enhance footer styling and update header title in index.html
- update Makefile and project configuration for improved run command and package management
- setup Python image upscaler with Real-ESRGAN, FastAPI, and uv (#1)

### Fix

- update test commands to use 'uv run' for consistency
- lint/format
