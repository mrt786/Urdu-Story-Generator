"""
Tests for the FastAPI Urdu Story Generator backend.
Run with:  pytest tests/ -v
"""

import sys
import os

# Ensure the backend and models directories are on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'models'))

from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


# ── Health check ──────────────────────────────────────
def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


# ── Root endpoint ─────────────────────────────────────
def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "status" in response.json()


# ── POST /generate (no prefix) ───────────────────────
def test_generate_no_prefix():
    response = client.post("/generate", json={"prefix": "", "max_length": 50})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert isinstance(data["story"], str)
    assert len(data["story"]) > 0


# ── POST /generate (with prefix) ─────────────────────
def test_generate_with_prefix():
    response = client.post(
        "/generate",
        json={"prefix": "ایک دن", "max_length": 50, "temperature": 0.8},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["prefix"] == "ایک دن"


# ── POST /generate (validation: max_length too large) ─
def test_generate_validation():
    response = client.post("/generate", json={"prefix": "", "max_length": 9999})
    # Pydantic should reject max_length > 5000
    assert response.status_code == 422


# ── GET /model-info ───────────────────────────────────
def test_model_info():
    response = client.get("/model-info")
    assert response.status_code == 200
    data = response.json()
    assert "vocabulary_size" in data
    assert "is_trained" in data
    assert data["model_type"] is not None
