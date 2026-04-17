FROM python:3.14-slim

WORKDIR /app

# Copy setup.py first for editable install
COPY setup.py .

# Copy and install rate_limiter package
COPY rate_limiter/ ./rate_limiter/
RUN pip install --no-cache-dir -e .

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend
COPY test_backend/ ./test_backend/

# Expose port
EXPOSE 8000

# Run with environment variable for Redis URL
CMD ["python", "-m", "uvicorn", "test_backend.main:app", "--host", "0.0.0.0", "--port", "8000"]