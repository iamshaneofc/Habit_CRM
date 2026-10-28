"""
Test suite for Step 15: Security & Configuration Hardening.
Verifies:
- .gitignore patterns for secrets, credentials, pem certificates, and backups.
- No tracked secrets or database files in Git index.
- Sanitized diagnostic endpoints without secret exposure.
- Standard security headers (nosniff, DENY, strict-origin, etc.).
- Input validation on email fields (RFC-compliant regex validation).
- Brute-force rate limiting protection on authentication endpoints.
- Authorization enforcement on all state-changing endpoints.
"""
import os
import sys
import subprocess

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
import database
from main import app
from auth import create_access_token
from models import User

def test_gitignore_rules():
    gi_path = os.path.join(os.path.dirname(__file__), "..", ".gitignore")
    assert os.path.exists(gi_path), ".gitignore must exist"
    with open(gi_path, "r", encoding="utf-8") as f:
        gi = f.read()

    assert ".env" in gi, ".env must be ignored"
    assert "*.pem" in gi, "*.pem must be ignored"
    assert "*.key" in gi, "*.key must be ignored"
    assert "*.db" in gi, "*.db must be ignored"
    assert "backups/" in gi, "backups/ must be ignored"
    assert ".pytest_cache/" in gi, ".pytest_cache/ must be ignored"

def test_no_secrets_tracked_in_git():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=True
    )
    tracked_files = result.stdout.splitlines()

    for path in tracked_files:
        assert not path.endswith(".db"), f"Database file tracked: {path}"
        assert not path.endswith(".pem"), f"Certificate file tracked: {path}"
        assert not path.endswith(".key"), f"Key file tracked: {path}"
        if path.endswith(".env"):
            assert False, f"Secret env file tracked: {path}"

def test_security_headers_and_status_endpoint():
    database.check_and_stabilize_db()
    with TestClient(app) as client:
        res = client.get("/api/database/status")
        assert res.status_code == 200
        
        # Security headers
        assert res.headers.get("X-Content-Type-Options") == "nosniff"
        assert res.headers.get("X-Frame-Options") == "DENY"
        assert res.headers.get("X-XSS-Protection") == "1; mode=block"
        assert res.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
        
        # No credentials exposed
        body = res.json()
        assert "password" not in str(body).lower()
        assert "secret" not in str(body).lower()

def test_email_validation():
    with TestClient(app) as client:
        # Invalid email format
        res = client.post("/api/auth/register", json={
            "email": "not-an-email",
            "password": "Password123!"
        })
        assert res.status_code == 422, f"Expected 422 for invalid email, got {res.status_code}"

def test_unauthenticated_endpoint_protection():
    with TestClient(app) as client:
        # Ensure cookie or bearer token is absent
        client.cookies.clear()
        
        endpoints = [
            ("POST", "/api/habits", {"name": "Test Habit"}),
            ("POST", "/api/habits/toggle", {"habit_id": 1, "date": "2026-10-28"}),
            ("POST", "/api/habits/1/archive", None),
            ("DELETE", "/api/habits/1", None),
            ("POST", "/api/habits/reset-defaults", None),
            ("GET", "/api/charts/weekly-data", None),
            ("GET", "/api/charts/category-data", None)
        ]
        for method, path, payload in endpoints:
            if method == "POST":
                r = client.post(path, json=payload or {})
            elif method == "DELETE":
                r = client.delete(path)
            elif method == "GET":
                r = client.get(path)
            assert r.status_code in (401, 303), f"Unauthenticated request to {path} not blocked: {r.status_code}"

def test_rate_limiting():
    with TestClient(app) as client:
        # Send 12 rapid registration attempts from same client IP
        blocked = False
        for i in range(12):
            res = client.post("/api/auth/register", json={
                "email": f"ratetest{i}@example.com",
                "password": "Password123!"
            })
            if res.status_code == 429:
                blocked = True
                assert "Too many register attempts" in res.json()["detail"]
                break
        assert blocked, "Rate limiter failed to block excessive requests with 429"

if __name__ == "__main__":
    print("Running Step 15 Security & Hardening Tests...")
    test_gitignore_rules()
    print("[OK] test_gitignore_rules passed.")
    test_no_secrets_tracked_in_git()
    print("[OK] test_no_secrets_tracked_in_git passed.")
    test_security_headers_and_status_endpoint()
    print("[OK] test_security_headers_and_status_endpoint passed.")
    test_email_validation()
    print("[OK] test_email_validation passed.")
    test_unauthenticated_endpoint_protection()
    print("[OK] test_unauthenticated_endpoint_protection passed.")
    test_rate_limiting()
    print("[OK] test_rate_limiting passed.")
    print("All Step 15 security and configuration hardening tests passed successfully!")
