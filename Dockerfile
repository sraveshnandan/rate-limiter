FROM python:3.14-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy rate_limiter package
COPY rate_limiter/ ./rate_limiter/
COPY setup.py .
RUN pip install --no-cache-dir -e .

# Copy backend
COPY test_backend/ ./test_backend/

# Expose port
EXPOSE 8000

# Run with environment variable for Redis URL
CMD ["python", "-m", "uvicorn", "test_backend.main:app", "--host", "0.0.0.0", "--port", "8000"]