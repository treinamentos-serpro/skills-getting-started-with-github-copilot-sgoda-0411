import unittest
from copy import deepcopy

from fastapi.testclient import TestClient

from src.app import activities, app


class UnregisterTests(unittest.TestCase):
    def setUp(self):
        self.original_activities = deepcopy(activities)
        self.client = TestClient(app)

    def tearDown(self):
        activities.clear()
        activities.update(self.original_activities)
        self.client.close()

    def test_unregister_removes_only_selected_participant(self):
        email = "michael@mergington.edu"
        response = self.client.delete(
            "/activities/Chess%20Club/unregister", params={"email": email}
        )
        self.assertEqual(response.status_code, 200)
        updated = self.client.get("/activities").json()
        self.assertEqual(updated["Chess Club"]["participants"], ["daniel@mergington.edu"])
        self.assertEqual(updated["Gym Class"], self.original_activities["Gym Class"])
        response = self.client.post(
            "/activities/Chess%20Club/signup", params={"email": email}
        )
        self.assertEqual(response.status_code, 200)

    def test_unregister_missing_participant_leaves_data_unchanged(self):
        response = self.client.delete(
            "/activities/Chess%20Club/unregister", params={"email": "missing@example.com"}
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(activities, self.original_activities)

    def test_unregister_missing_activity_leaves_data_unchanged(self):
        response = self.client.delete(
            "/activities/Missing/unregister", params={"email": "michael@mergington.edu"}
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(activities, self.original_activities)