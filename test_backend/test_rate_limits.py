import requests
import time

BASE_URL = "http://127.0.0.1:8000/api"

print("Starting Rate Limiter Automated Tests...")
print("-" * 50)

def test_basic_endpoint():
    print("Testing /api/basic (Limit: 4 requests per 20s per endpoint)")
    success_count = 0
    throttled_count = 0
    
    for i in range(6):
        response = requests.get(f"{BASE_URL}/basic")
        if response.status_code == 200:
            success_count += 1
            print(f"[{i+1}] 🟢 200 OK - Remaining: {response.headers.get('ratelimit-remaining')}")
        elif response.status_code == 429:
            throttled_count += 1
            print(f"[{i+1}] 🔴 429 Too Many Requests - Retry After: {response.headers.get('retry-after')}s")
        else:
            print(f"[{i+1}] 🟡 Unexpected status: {response.status_code}")
            
    print(f"Summary for /basic: {success_count} succeeded, {throttled_count} throttled.")
    print("-" * 50)

def test_custom_key_endpoint():
    print("Testing /api/custom with different users")
    
    # User 1 sends requests until throttled
    print("User 1 (user-A) sending 5 requests:")
    headers_user_a = {"x-user-id": "user-A"}
    for i in range(5):
        response = requests.get(f"{BASE_URL}/custom", headers=headers_user_a)
        status = "🟢 200 OK" if response.status_code == 200 else "🔴 429 Throttled"
        print(f"  User A [{i+1}] -> {status}")
        
    print("\nNow User 2 (user-B) sends a request. They shouldn't be throttled.")
    headers_user_b = {"x-user-id": "user-B"}
    response = requests.get(f"{BASE_URL}/custom", headers=headers_user_b)
    status = "🟢 200 OK" if response.status_code == 200 else "🔴 429 Throttled"
    print(f"  User B [1] -> {status}")
    print("-" * 50)

def test_health_skip():
    print("Testing /api/health (Should be skipped by rate limiter)")
    success_count = 0
    for i in range(10):
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            success_count += 1
            
    print(f"Sent 10 requests to /health. Succeeded: {success_count}/10")
    if success_count == 10:
        print("🟢 Health endpoint successfully bypassed the rate limiter!")
    print("-" * 50)

if __name__ == "__main__":
    test_basic_endpoint()
    test_custom_key_endpoint()
    test_health_skip()
    print("Tests completed!")
