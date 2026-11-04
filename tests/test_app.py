from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture
def client():
    original_activities = deepcopy(activities)
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        activities.clear()
        activities.update(original_activities)


def test_get_activities_returns_all_activities(client):
    # Arrange
    expected_activities = deepcopy(activities)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == expected_activities


def test_signup_adds_participant(client):
    # Arrange
    activity_name = "Volleyball Club"
    email = "new.student@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup", params={"email": email}
    )
    activities_response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {email} for {activity_name}"
    }
    assert email in activities_response.json()[activity_name]["participants"]


def test_signup_returns_404_for_missing_activity(client):
    # Arrange
    activity_name = "Missing Activity"
    email = "new.student@mergington.edu"
    original_activities = deepcopy(activities)

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert activities == original_activities


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    original_participants = deepcopy(activities[activity_name]["participants"])

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"
    assert activities[activity_name]["participants"] == original_participants


def test_unregister_removes_only_selected_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    original_other_activity = deepcopy(activities["Gym Class"])

    # Act
    response = client.delete(
        f"/activities/{activity_name}/unregister", params={"email": email}
    )
    updated = client.get("/activities").json()

    # Assert
    assert response.status_code == 200
    assert updated[activity_name]["participants"] == ["daniel@mergington.edu"]
    assert updated["Gym Class"] == original_other_activity


def test_unregister_returns_404_for_missing_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "missing@example.com"
    original_activities = deepcopy(activities)

    # Act
    response = client.delete(
        f"/activities/{activity_name}/unregister", params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert activities == original_activities


def test_unregister_returns_404_for_missing_activity(client):
    # Arrange
    activity_name = "Missing Activity"
    email = "michael@mergington.edu"
    original_activities = deepcopy(activities)

    # Act
    response = client.delete(
        f"/activities/{activity_name}/unregister", params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert activities == original_activities