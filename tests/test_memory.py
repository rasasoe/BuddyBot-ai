import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_save_memory():
    response = client.post("/memory/save", json={"key": "test_key", "value": "test_value"})
    assert response.status_code == 200

def test_get_memory():
    client.post("/memory/save", json={"key": "test_key", "value": "test_value"})
    response = client.get("/memory/get?key=test_key")
    assert response.status_code == 200
    data = response.json()
    assert data["key"] == "test_key"
    assert data["value"] == "test_value"