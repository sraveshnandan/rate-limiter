FROM python:3.14-slim

WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy rate_limiter package
COPY rate_limiter/ ./rate_limiter/

# Copy test_backend
COPY test_backend/ ./test_backend/

# Expose port
EXPOSE 8000

# Run directly with python -m
CMD ["python", "-c", "import sys; sys.path.insert(0, '.'); from test_backend.main import app; import uvicorn; uvicorn.run(app, host='0.0.0.0', port=8000)"]