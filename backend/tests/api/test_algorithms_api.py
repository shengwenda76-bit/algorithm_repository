from fastapi.testclient import TestClient

from app.main import app


def test_list_algorithms():
    client = TestClient(app)
    resp = client.get("/v1/algorithms")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data["categories"], list)
    assert isinstance(data["categories"][0]["algorithms"], list)


def test_get_algorithm_version_schema():
    client = TestClient(app)
    resp = client.get("/v1/algorithms/missing_value/versions/1.0.0")
    assert resp.status_code == 200
    data = resp.json()
    assert "input_schema" in data
    assert "output_schema" in data
