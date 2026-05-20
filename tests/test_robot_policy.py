import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_robot_status():
    response = client.get("/robot/status")
    assert response.status_code == 200
    data = response.json()
    assert "battery" in data

def test_status_command():
    response = client.post("/robot/command", json={"command": "status"})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True

def test_robot_control_command_blocked():
    response = client.post("/robot/command", json={"command": "stop"})
    assert response.status_code == 403
    assert "locally on the Pi" in response.json()["detail"]

def test_navigation_command_blocked():
    response = client.post("/nav/go", json={"name": "kitchen"})
    assert response.status_code == 403
    assert "locally on the Pi" in response.json()["detail"]

def test_unsafe_command():
    response = client.post("/robot/command", json={"command": "disable_estop"})
    assert response.status_code == 403
