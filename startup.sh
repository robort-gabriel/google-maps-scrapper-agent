#!/bin/bash

# Google Maps Scraper FastAPI Startup Script
# Uses Poetry for dependency management

# Set default values
HOST=${HOST:-0.0.0.0}
PORT=${PORT:-${COOLIFY_PORT:-8000}}
WORKERS=${WORKERS:-5}
TIMEOUT=${TIMEOUT:-6000}

# Ensure output directory exists
mkdir -p output

# Start the FastAPI application with Gunicorn
echo "Starting Google Maps Scraper API on ${HOST}:${PORT} with ${WORKERS} workers..."
exec poetry run gunicorn \
    -w ${WORKERS} \
    -k uvicorn.workers.UvicornWorker \
    -b ${HOST}:${PORT} \
    --timeout ${TIMEOUT} \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    main:app
