

# Start the FastAPI application
gunicorn -w 5 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 --timeout 6000 app:app

