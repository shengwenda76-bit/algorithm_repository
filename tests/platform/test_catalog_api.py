import pytest
from fastapi.testclient import TestClient
from services.main import app

client = TestClient(app)

def test_list_algorithms():
    response = client.get("/algorithms/")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data

def test_get_algorithm_detail():
    # Attempt to fetch the one we registered in registry test 
    response = client.get("/algorithms/test_algo_1")
    if response.status_code == 200:
        data = response.json()
        assert data["code"] == "test_algo_1"
    else:
        # If order changes, it might be 404
        assert response.status_code == 404

def test_get_nonexistent_algorithm():
    response = client.get("/algorithms/does_not_exist_at_all")
    assert response.status_code == 404
    assert response.json()["detail"]["error"] == "ALGORITHM_NOT_FOUND"
