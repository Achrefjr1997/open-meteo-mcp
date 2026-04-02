# Open-Meteo MCP Server Docker Image
# Multi-stage build for optimized production image

# ==================== Build Stage ====================
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY requirements.txt .
COPY pyproject.toml .

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ==================== Production Stage ====================
FROM python:3.11-slim AS production

WORKDIR /app

# Create non-root user for security
RUN groupadd --gid 1000 appgroup && \
    useradd --uid 1000 --gid appgroup --shell /bin/bash --create-home appuser

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY --chown=appuser:appgroup src/ src/
COPY --chown=appuser:appgroup README.md .
COPY --chown=appuser:appgroup QUICKSTART.md .

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    OPEN_METEO_TIMEZONE=GMT \
    OPEN_METEO_TIMEOUT=30.0 \
    OPEN_METEO_RATE_LIMIT=0.1

# Switch to non-root user
USER appuser

# Expose port for SSE transport
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health')" || exit 1

# Default command runs with stdio transport (for MCP clients)
CMD ["python", "-m", "src.server"]

# ==================== Development Stage ====================
FROM production AS development

USER root

# Install development dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install dev dependencies
COPY --chown=appuser:appgroup requirements.txt .
RUN pip install --no-cache-dir pytest pytest-asyncio black ruff mypy

# Copy test directory
COPY --chown=appuser:appgroup tests/ tests/

USER appuser

# Default command for development
CMD ["python", "-m", "pytest", "tests/", "-v"]
