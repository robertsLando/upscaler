# Multi-stage Dockerfile for upscaler
# Supports both CLI and webserver modes

# Stage 1: Builder
FROM python:3.12-slim AS builder

# Set working directory
WORKDIR /app

# Install system dependencies for building
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files first for better caching
COPY pyproject.toml ./

# Copy source code
COPY src/ src/

# Install dependencies and the package
RUN pip install --no-cache-dir --user -e .

# Stage 2: Runtime
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy only the necessary files from builder
COPY --from=builder /root/.local /root/.local
COPY --from=builder /app/src /app/src
COPY --from=builder /app/pyproject.toml /app/pyproject.toml

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Set up PYTHONPATH
ENV PYTHONPATH=/app/src

# Create directory for input/output images (for CLI usage)
RUN mkdir -p /images

# Set working directory for images
WORKDIR /images

# Expose port for webserver
EXPOSE 8000

# Default command runs the webserver
# Override with CLI commands as needed
CMD ["python", "-m", "upscaler"]
