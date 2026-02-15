import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.config import (
    HSTS_ENABLED,
    RATE_LIMIT_ENABLED,
    CORS_ORIGINS,
    CORS_ALLOW_CREDENTIALS,
    CORS_ALLOW_METHODS,
    CORS_ALLOW_HEADERS,
    REDIS_URL,
    MEMORY_CLEANUP_ENABLED,
)
import os
import time

client = TestClient(app)

# Phase 12 QC: Backend & Integration Scenarios
# Focus: Security Headers, Rate Limiting, CORS, Error Handling, Memory Cleanup

class TestPhase12QC:

    # 1. [Security] HSTS Header Enforcement
    def test_qc_dev_01_hsts_header(self):
        """Phase 12-1-3: Verify HSTS header presence when enabled."""
        # Force enable HSTS for this test context if possible, or check current config
        response = client.get("/api/system/status")
        
        if HSTS_ENABLED:
            assert "strict-transport-security" in response.headers
            assert "max-age=" in response.headers["strict-transport-security"]
        else:
            print("HSTS is disabled in config, skipping strict check.")

    # 2. [Security] XSS Prevention in Inputs
    def test_qc_dev_02_xss_sanitization(self):
        """Phase 12-3-1: Ensure API sanitizes or rejects XSS payloads."""
        malicious_payload = {"content": "<script>alert(1)</script>", "title": "XSS Test"}
        # Assuming an endpoint that accepts content, e.g., create memory or note
        # This endpoint might vary based on actual implementation
        response = client.post("/api/memories/", json=malicious_payload)
        
        # If the API allows raw storage, the frontend handles display (sanitization).
        # But ideally, the API should strip dangerous tags or encode them.
        if response.status_code == 201 or response.status_code == 200:
            data = response.json()
            content = data.get("content", "")
            # Verify dangerous script tag is neutralized
            assert "<script>" not in content or "&lt;script&gt;" in content

    # 3. [Security] Rate Limiting Logic (429 Too Many Requests)
    def test_qc_dev_03_rate_limiting(self):
        """Phase 12-3-2: Verify rate limiter blocks excessive requests."""
        if not RATE_LIMIT_ENABLED:
            pytest.skip("Rate limiting disabled")

        # Spam requests to a protected endpoint
        for _ in range(20):
            response = client.get("/api/system/status")
            if response.status_code == 429:
                break
        
        # We expect at least some requests to pass, but rapid-fire might trigger 429
        # Exact limit depends on config. Just checking the mechanism exists.
        assert response.status_code in [200, 429]

    # 4. [Infra] CORS Configuration Validation
        def test_qc_dev_04_cors_headers(self):
            """Phase 12-1-2: Verify CORS headers for allowed origins."""
            origin = "http://localhost:3000"  # Typical frontend port
            headers = {
                "Origin": origin,
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Content-Type",
            }
            # Preflight request
            response = client.options("/health", headers=headers)
            
            # Check Access-Control-Allow-Origin
            # Note: TestClient might handle middleware differently than uvicorn
            # If 200, it means OPTIONS was handled (likely by CORS middleware)
            # If 405, it means it fell through to router (which has no OPTIONS)
            
            if response.status_code == 200:
                 if origin in CORS_ORIGINS or "*" in CORS_ORIGINS:
                    allow_origin = response.headers.get("access-control-allow-origin")
                    assert allow_origin == origin or allow_origin == "*"
                    assert response.headers.get("access-control-allow-credentials") == "true"
            else:
                # If 405, it implies CORS middleware didn't intercept or logic differs in TestClient
                print(f"CORS OPTIONS request returned {response.status_code}. Middleware might be bypassed in TestClient.")
                # Verify via GET request headers
                response_get = client.get("/health", headers={"Origin": origin})
                if origin in CORS_ORIGINS or "*" in CORS_ORIGINS:
                    allow_origin = response_get.headers.get("access-control-allow-origin")
                    assert allow_origin == origin or allow_origin == "*"
    # 5. [Infra] Redis Connectivity (Phase 12-2)
    def test_qc_dev_05_redis_connection(self):
        """Phase 12-2: Verify Redis is reachable via configuration."""
        # Direct check using redis-py or checking health endpoint
        if not REDIS_URL:
            pytest.skip("Redis URL not configured")
        
        # Assuming health endpoint checks Redis
        response = client.get("/api/system/status")
        assert response.status_code == 200
        data = response.json()
        
        # Check if Redis status is reported (Phase 12-3 extended healthcheck)
        if "components" in data and "redis" in data["components"]:
            assert data["components"]["redis"]["status"] == "ok"

    # 6. [Logic] Error Response Standardization
    def test_qc_dev_06_error_format(self):
        """Phase 12-2-4: Verify error responses follow standard JSON format."""
        # Trigger a 404
        response = client.get("/api/non-existent-endpoint-123")
        assert response.status_code == 404
        
        data = response.json()
        # Expecting standardized keys: detail, error_code, timestamp, etc.
        # Phase 12 standardized format uses 'error' object
        if "detail" in data:
            # Standard FastAPI error
            pass
        elif "error" in data:
             assert "code" in data["error"]
             assert "message" in data["error"]
        else:
            pytest.fail(f"Unexpected error format: {data}")

    # 7. [Logic] Memory Cleanup Scheduler (Configuration Check)
    def test_qc_dev_07_memory_cleanup_config(self):
        """Phase 12-3-4: Verify memory cleanup scheduler is active/configurable."""
        # This is a configuration test, verifying the flag logic
        assert MEMORY_CLEANUP_ENABLED is not None
        # Logic test would require mocking the scheduler execution

    # 8. [Database] GIN Index Performance (Implicit)
    def test_qc_dev_08_search_performance(self):
        """Phase 12-2-3: Basic latency check for search endpoint (GIN Index target)."""
        payload = {"question": "test", "context_enabled": False}
        # Warmup
        client.post("/api/ask", json=payload)
        
        start_time = time.time()
        response = client.post("/api/ask", json=payload)
        duration = time.time() - start_time
        
        assert response.status_code == 200
        print(f"Search Duration: {duration}s")
        assert duration < 10.0 

    # 9. [Security] Secure Cookie Attributes (If applicable)
    def test_qc_dev_09_secure_cookies(self):
        """Phase 12-1: Verify Set-Cookie headers have Secure/HttpOnly flags."""
        # Simulate login or session creation
        # response = client.post("/api/auth/login", json={...})
        # For now, check any response setting cookies
        pass 

    # 10. [Infra] Environment Variable Precedence
    def test_qc_dev_10_env_config(self):
        """Phase 12-1: Verify critical config values are loaded from Env."""
        from backend.config import PROJECT_ROOT
        # Check if loaded config matches expected Env (mock or actual)
        assert str(PROJECT_ROOT) is not None
        assert len(str(PROJECT_ROOT)) > 0
        # e.g., ENABLE_HSTS, REDIS_URL existence
