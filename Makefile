.PHONY: help install dev-install test lint format clean run docker-build docker-run generate-logo

help:
	@echo "Available commands:"
	@echo "  make install      - Install dependencies using uv"
	@echo "  make dev-install  - Install dev dependencies"
	@echo "  make test         - Run tests with pytest"
	@echo "  make lint         - Run linters (ruff, black check)"
	@echo "  make format       - Format code with black and ruff"
	@echo "  make format-html  - Format HTML with prettier"
	@echo "  make clean        - Clean up cache and temporary files"
	@echo "  make run          - Run the application"
	@echo "  make docker-build - Build Docker image"
	@echo "  make docker-run   - Run Docker container"
	@echo "  make generate-logo - Generate all logo assets from source logo"

install:
	uv sync
# Install package in editable mode, -e flag creates a link to your source code, so changes are immediately available without reinstalling
	uv pip install -e .

test:
	uv run pytest tests/ -v

test-cov:
	uv run pytest tests/ --cov=src/upscaler --cov-report=html --cov-report=term --cov-report=xml

lint:
	uv run ruff check src/ tests/
	uv run black --check src/ tests/

format:
	uv run black src/ tests/
	uv run ruff check --fix src/ tests/

format-html:
	@command -v prettier >/dev/null 2>&1 && prettier --write "src/upscaler/templates/**/*.html" || echo "prettier not installed. Install with: npm install -g prettier"

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache .coverage htmlcov

run:
	uv run python -m upscaler

docker-build:
	docker build -t upscaler:latest .

docker-run:
	docker run -p 8000:8000 upscaler:latest

generate-logo:
	@echo "Generating logo assets from source logo..."
	@uv run python scripts/generate_logo_assets.py
	@echo ""
	@echo "✅ Logo assets generated!"
	@echo "To use a custom logo:"
	@echo "  1. Replace assets/logo/panda-logo.png with your 512x512 logo"
	@echo "  2. Run: make generate-logo"
