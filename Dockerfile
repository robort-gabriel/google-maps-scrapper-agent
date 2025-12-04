# Multi-stage Dockerfile for Google Maps Scraper FastAPI Application

# Stage 1: Build stage
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry==1.8.4

# Configure Poetry: Don't create virtualenv, don't ask questions
RUN poetry config virtualenvs.create false

# Set work directory
WORKDIR /app

# Copy Poetry files
COPY pyproject.toml poetry.lock* ./

# Install dependencies
RUN poetry install --no-interaction --no-ansi --only=main || \
    poetry install --no-interaction --no-ansi --no-dev

# Stage 2: Runtime stage
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/usr/local/bin:$PATH" \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# Install system dependencies for Playwright and runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Playwright dependencies
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libcairo2 \
    libatspi2.0-0 \
    libxshmfence1 \
    # Other utilities
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Set work directory
WORKDIR /app

# Copy application code
COPY . .

# Install Playwright browsers (Chromium only)
RUN playwright install chromium && \
    playwright install-deps chromium

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run Gunicorn with Uvicorn workers
CMD ["gunicorn", "-w", "5", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "--timeout", "6000", "--access-logfile", "-", "--error-logfile", "-", "main:app"]

