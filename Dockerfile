FROM python:3.14-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy rate_limiter package
COPY rate_limiter/ ./rate_limiter/
COPY setup.py .

# Install rate_limiter package
RUN pip install --no-cache-dir -e .

# Copy test_backend
COPY test_backend/ ./test_backend/

# Expose port
EXPOSE 8000

# Run backend
CMD ["python", "test_backend/main.py"]