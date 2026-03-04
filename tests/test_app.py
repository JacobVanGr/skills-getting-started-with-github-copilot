import pytest
from fastapi.testclient import TestClient
from src.app import app
import copy

@pytest.fixture
def client():
    # Use a fresh client for each test
    return TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities(monkeypatch):
    # Arrange: Reset the activities dict before each test for isolation
    from src import app as app_module
    original = copy.deepcopy(app_module.activities)
    yield
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(original))

def test_get_activities(client):
    # Arrange
    # Act
    response = client.get("/activities")
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]

def test_signup_success(client):
    # Arrange
    email = "newstudent@mergington.edu"
    activity = "Chess Club"
    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")
    # Assert
    assert response.status_code == 200
    assert email in client.get("/activities").json()[activity]["participants"]

def test_signup_duplicate(client):
    # Arrange
    email = "michael@mergington.edu"  # Already in Chess Club
    activity = "Chess Club"
    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")
    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"].lower()

def test_signup_nonexistent_activity(client):
    # Arrange
    email = "ghost@mergington.edu"
    activity = "Nonexistent Club"
    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")
    # Assert
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_unreg_success(client):
    # Arrange
    email = "michael@mergington.edu"
    activity = "Chess Club"
    # Act
    response = client.delete(f"/activities/{activity}/unregister?email={email}")
    # Assert
    assert response.status_code == 200
    assert email not in client.get("/activities").json()[activity]["participants"]

def test_unreg_nonexistent_participant(client):
    # Arrange
    email = "ghost@mergington.edu"
    activity = "Chess Club"
    # Act
    response = client.delete(f"/activities/{activity}/unregister?email={email}")
    # Assert
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_unreg_nonexistent_activity(client):
    # Arrange
    email = "ghost@mergington.edu"
    activity = "Nonexistent Club"
    # Act
    response = client.delete(f"/activities/{activity}/unregister?email={email}")
    # Assert
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_signup_when_full(client):
    # Arrange
    activity = "Math Olympiad"
    # Fill up the activity
    for i in range(10):
        email = f"student{i}@mergington.edu"
        client.post(f"/activities/{activity}/signup?email={email}")
    # Act
    response = client.post(f"/activities/{activity}/signup?email=overflow@mergington.edu")
    # Assert
    assert response.status_code == 400 or response.status_code == 409
    # Accept either 400 or 409 for full
    assert "full" in response.json()["detail"].lower() or "max" in response.json()["detail"].lower()

# TODO: Add more tests for static file serving, input validation, etc.
