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

# Stage 2: Production stage
FROM python:3.11-slim as production

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/usr/local/bin:$PATH" \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright \
    PORT=8000

# Install system dependencies for Playwright and runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Playwright Chromium dependencies
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
    # Additional Chromium dependencies
    fonts-liberation \
    fonts-noto-color-emoji \
    fonts-unifont \
    libgtk-3-0 \
    libvulkan1 \
    xdg-utils \
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

# Install Playwright browsers (Chromium only) as root
# Note: We skip install-deps since we already installed dependencies above
RUN playwright install chromium

# Create necessary directories with proper permissions
RUN mkdir -p /app/output /app/logs /ms-playwright \
    && chown -R appuser:appuser /app /ms-playwright

# Create user home directory and set proper permissions
RUN mkdir -p /home/appuser \
    && chown -R appuser:appuser /home/appuser

# Ensure permissions are correct for site-packages
RUN chown -R appuser:appuser /usr/local/lib/python3.11/site-packages

# Set environment variables for user directories
ENV HOME=/home/appuser
ENV PYTHONUSERBASE=/home/appuser/.local

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
# Healthcheck may be enabled by orchestrator separately

# Use exec form for proper signal handling
CMD ["gunicorn", "-w", "5", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "--timeout", "6000", "--access-logfile", "-", "--error-logfile", "-", "main:app"]

