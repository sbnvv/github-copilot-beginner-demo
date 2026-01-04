import copy
import urllib.parse

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    # Make a deep copy and restore after each test to avoid state leakage
    backup = copy.deepcopy(activities)
    try:
        yield
    finally:
        activities.clear()
        activities.update(copy.deepcopy(backup))


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Soccer Team" in data


def test_signup_success():
    activity = "Soccer Team"
    email = "testuser@example.com"

    assert email not in activities[activity]["participants"]

    resp = client.post(f"/activities/{urllib.parse.quote(activity)}/signup?email={urllib.parse.quote(email)}")

    assert resp.status_code == 200
    body = resp.json()
    assert "Signed up" in body.get("message", "")
    assert email in activities[activity]["participants"]


def test_signup_duplicate_returns_400():
    activity = "Soccer Team"
    email = activities[activity]["participants"][0]

    resp = client.post(f"/activities/{urllib.parse.quote(activity)}/signup?email={urllib.parse.quote(email)}")
    assert resp.status_code == 400


def test_unregister_success():
    activity = "Soccer Team"
    email = activities[activity]["participants"][0]

    resp = client.delete(f"/activities/{urllib.parse.quote(activity)}/unregister?email={urllib.parse.quote(email)}")
    assert resp.status_code == 200
    body = resp.json()
    assert "Unregistered" in body.get("message", "")
    assert email not in activities[activity]["participants"]


def test_unregister_not_registered_returns_404():
    activity = "Soccer Team"
    email = "not-registered@example.com"

    resp = client.delete(f"/activities/{urllib.parse.quote(activity)}/unregister?email={urllib.parse.quote(email)}")
    assert resp.status_code == 404
