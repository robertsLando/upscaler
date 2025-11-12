# GitHub Copilot Instructions for Image Upscaler

## Project Overview
This is a Python web application that provides AI-powered image upscaling using Real-ESRGAN. The application is built with FastAPI and uses the uv package manager for dependency management.

## Architecture & Structure
- **Package Structure**: Follow Python packaging standards with source code in `src/upscaler/`
- **Framework**: FastAPI for web API with uvicorn server
- **AI Model**: Real-ESRGAN x4plus for image upscaling (lazy loaded)
- **Templates**: HTML templates stored in `src/upscaler/templates/`
- **Tests**: Pytest-based tests in `tests/` directory

## Development Guidelines

### Code Style
- **Linting**: Use ruff for Python linting (configured in `pyproject.toml`)
- **Formatting**: Use black for code formatting (line length: 100)
- **HTML/CSS/JS**: Use prettier for formatting (configured in `.prettierrc`)
- **Imports**: Keep imports organized (stdlib → third-party → local)

### Commit Messages
Follow the [Conventional Commits](https://www.conventionalcommits.org/) standard for all commit messages:
- **Format**: `<type>(<scope>): <description>`
- **Types**:
  - `feat`: New feature
  - `fix`: Bug fix
  - `docs`: Documentation changes
  - `style`: Code style changes (formatting, missing semicolons, etc.)
  - `refactor`: Code refactoring without changing functionality
  - `perf`: Performance improvements
  - `test`: Adding or updating tests
  - `build`: Changes to build system or dependencies
  - `ci`: CI/CD configuration changes
  - `chore`: Other changes that don't modify src or test files
- **Scope**: Optional, indicates the area affected (e.g., `api`, `upscaler`, `tests`, `makefile`)
- **Examples**:
  - `feat(api): add batch upload endpoint`
  - `fix(upscaler): resolve memory leak in model loading`
  - `docs: update installation instructions`
  - `test(api): add tests for error handling`
  - `chore(deps): update torch to 2.4.1`

### Testing
- Write unit tests for core logic functions
- Write integration tests for API endpoints using FastAPI TestClient
- Mark slow tests (requiring AI model) with `@pytest.mark.slow`
- Maintain test coverage above 80%
- Run tests with: `make test` or `PYTHONPATH=src pytest tests/ -v`
- **CRITICAL**: When making changes to `src/upscaler/upscaler.py` or `src/upscaler/app.py`, ALWAYS run an end-to-end test to verify that image upscaling works correctly. This ensures the AI model integration is not broken.

### API Design
- Use FastAPI's dependency injection and validation
- Return appropriate HTTP status codes
- Include proper error messages in HTTPException
- Document endpoints with docstrings
- Validate input parameters (e.g., image dimensions: 1-10000 pixels)

### Configuration
- Use `pyproject.toml` for project configuration
- Pin critical dependencies (torch, torchvision) for compatibility
- Use uv for dependency management and lock files

### Performance
- Lazy load the Real-ESRGAN model (only on first upscale request)
- Use CPU by default (GPU support configurable via `gpu_id` parameter)
- Preserve aspect ratio when resizing images

### Makefile Commands
- `make install`: Install dependencies with uv
- `make test`: Run test suite
- `make lint`: Check code with linters
- `make format`: Auto-format code
- `make run`: Start the application
- `make clean`: Remove cache and temporary files

## Key Files
- `src/upscaler/app.py`: FastAPI application and routes
- `src/upscaler/upscaler.py`: Core upscaling logic with Real-ESRGAN
- `src/upscaler/templates/index.html`: Web UI
- `tests/test_api.py`: API integration tests
- `tests/test_upscaler.py`: Unit tests for upscaling logic
- `pyproject.toml`: Project configuration and dependencies
- `Makefile`: Development workflow commands

## Common Patterns

### Adding New Endpoints
```python
@app.post("/endpoint")
async def endpoint_handler(
    param: type = Form(...),
    file: UploadFile = File(...)
):
    """Docstring explaining the endpoint."""
    # Validate inputs
    if validation_fails:
        raise HTTPException(status_code=400, detail="Error message")
    
    # Process and return
    return {"result": "data"}
```

### Image Processing
- Always convert images to RGB mode
- Use numpy arrays for AI model processing
- Use PIL Image for resizing and format conversion
- Save output as PNG format

### Error Handling
- Catch exceptions and log them
- Return user-friendly error messages
- Use appropriate HTTP status codes (400 for validation, 500 for server errors)

## Dependencies to Know
- **fastapi**: Web framework
- **uvicorn**: ASGI server
- **pillow**: Image processing
- **numpy**: Array operations
- **realesrgan**: AI upscaling model
- **basicsr**: Base SR framework (dependency of realesrgan)
- **torch/torchvision**: ML framework (pinned versions for compatibility)

## Compatibility Notes
- Patch `torchvision.transforms.functional_tensor` import for basicsr compatibility
- Use torch < 2.5 and torchvision < 0.20 for stability
- Python 3.12+ required

## When Making Changes
1. Run linters before committing: `make lint`
2. Format code: `make format`
3. Run tests: `make test`
4. **If modifying upscaler core files** (`src/upscaler/upscaler.py` or `src/upscaler/app.py`): Run full test suite including slow tests with `PYTHONPATH=src pytest tests/ -v` to ensure end-to-end image upscaling still works
5. Update tests when changing validation logic
6. Update README when adding new features or commands
7. Keep the Makefile up to date with new commands
