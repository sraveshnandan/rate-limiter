# Test Backend Guide

This directory contains a FastAPI-based test server designed to demonstrate and verify the functionality of the `rate-limiter` library.

## 1. Setup

Navigate to the `test_backend` directory and install the dependencies:

```bash
cd test_backend
pip install -r requirements.txt
```

### Environment Variables
Create a `.env` file in the `test_backend` directory (if it doesn't exist) and add your Gemini API key (optional, for AI analysis feature):

```env
GEMINI_API_KEY=your_api_key_here
```

## 2. Running the Server

Start the FastAPI server using `uvicorn`:

```bash
python main.py
```
The server will be available at `http://127.0.0.1:8000`.

## 3. Running Automated Tests

A separate script is provided to test the various rate-limiting scenarios:

```bash
python test_rate_limits.py
```

## 4. How It Works

### Integration
The rate limiter is integrated as a middleware in `main.py`:

```python
from rate_limiter.adapters.fastapi_adapter import RateLimiterMiddleware

app.add_middleware(RateLimiterMiddleware, limiter=limiter)
```

### Custom Key Generation
It uses a custom function to identify users by the `x-user-id` header if present, otherwise falling back to the client's IP:

```python
def custom_key_generator(request: Request):
    user_id = request.headers.get("x-user-id")
    return user_id if user_id else request.client.host
```

### Skip Rules
Certain requests can bypass the rate limiter (e.g., `/api/health` and CORS preflight requests):

```python
def skip_rules(request: Request):
    if request.method == "OPTIONS": return True
    return request.url.path == "/api/health"
```

### Multiple Limit Tiers
The backend demonstrates tiered rate limiting:
- **Global**: 10 requests per 60 seconds across all endpoints.
- **Endpoint-specific**: 4 requests per 20 seconds for each individual endpoint.

### AI Analysis (Bonus)
The `/api/analyze` endpoint uses Google Gemini to analyze rate limiter metrics and provide security insights based on throttled vs. allowed requests.
