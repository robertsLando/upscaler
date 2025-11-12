.PHONY: help install dev-install test lint format clean run

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

install:
	uv sync

dev-install:
	uv add --dev pytest pytest-cov ruff black

test:
	PYTHONPATH=src uv run pytest tests/ -v

test-cov:
	PYTHONPATH=src uv run pytest tests/ --cov=src/upscaler --cov-report=html --cov-report=term

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
	PYTHONPATH=src uv run python -m upscaler
