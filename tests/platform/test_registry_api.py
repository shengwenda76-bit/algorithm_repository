import pytest
from fastapi.testclient import TestClient
from services.library_platform.main import app

client = TestClient(app)

valid_payload = {
    "definition": {
        "code": "test_algo_1",
        "name": "Test Algorithm 1",
        "version": "1.0.0",
        "entrypoint": "test_algo_1.module:main",
        "category": "Testing",
        "inputs": [],
        "outputs": [],
        "params": [],
        "resources": {},
        "requirements": [],
        "tags": []
    },
    "artifact": {
        "package_name": "test-algo-1",
        "package_version": "1.0.0",
        "repository_url": "http://test-pypi",
        "artifact_type": "wheel",
        "filename": "test_algo_1-1.0.0.whl",
        "sha256": "abc"
    }
}

def test_health():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_register_algorithm():
    # Attempt to register
    response = client.post("/algorithms/register", json=valid_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["code"] == "test_algo_1"
    assert data["version"] == "1.0.0"

def test_register_duplicate():
    # First time might be from previous test, let's change version
    payload2 = valid_payload.copy()
    payload2["definition"]["version"] = "1.0.1"
    
    # Register 1.0.1
    client.post("/algorithms/register", json=payload2)
    
    # Register 1.0.1 again -> duplicate
    response = client.post("/algorithms/register", json=payload2)
    assert response.status_code == 409
    assert response.json()["detail"]["error"] == "DUPLICATE_VERSION"
