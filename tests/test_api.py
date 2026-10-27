import requests

from tests.conftest import BASE_URL, unique_username

EVENT_DATE = "2030-01-15T18:00:00"


def create_event(headers, **overrides):
    body = {"title": "Test Event", "date": EVENT_DATE, "location": "Berlin", **overrides}
    return requests.post(f"{BASE_URL}/api/events", json=body, headers=headers)


# Happy paths

def test_health_endpoint_returns_healthy():
    response = requests.get(f"{BASE_URL}/api/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_register_user_creates_new_user():
    username = unique_username()
    response = requests.post(
        f"{BASE_URL}/api/auth/register",
        json={"username": username, "password": "secret123"},
    )

    assert response.status_code == 201
    assert response.json()["user"]["username"] == username


def test_login_returns_jwt_token(user_credentials):
    response = requests.post(f"{BASE_URL}/api/auth/login", json=user_credentials)

    assert response.status_code == 200
    assert response.json()["access_token"]


def test_create_public_event_requires_auth_and_succeeds_with_token(auth_headers):
    response = create_event(auth_headers, title="Public Meetup")

    assert response.status_code == 201
    event = response.json()
    assert event["title"] == "Public Meetup"
    assert event["date"] == EVENT_DATE
    assert event["location"] == "Berlin"
    assert event["is_public"] is True


def test_rsvp_to_public_event_succeeds_without_auth(auth_headers):
    event_id = create_event(auth_headers).json()["id"]

    response = requests.post(f"{BASE_URL}/api/rsvps/event/{event_id}", json={"attending": True})

    assert response.status_code == 201
    assert response.json()["event_id"] == event_id


# Errors / edge cases

def test_register_duplicate_username_returns_400():
    creds = {"username": unique_username(), "password": "secret123"}
    first = requests.post(f"{BASE_URL}/api/auth/register", json=creds)
    second = requests.post(f"{BASE_URL}/api/auth/register", json=creds)

    assert first.status_code == 201
    assert second.status_code == 400
    assert second.json()["error"] == "Username already exists"


def test_login_with_wrong_password_returns_401(user_credentials):
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"username": user_credentials["username"], "password": "wrong-password"},
    )

    assert response.status_code == 401


def test_create_event_without_auth_returns_401():
    response = create_event(headers={})

    assert response.status_code == 401


def test_rsvp_to_private_event_without_auth_returns_401(auth_headers):
    event_id = create_event(auth_headers, is_public=False).json()["id"]

    response = requests.post(f"{BASE_URL}/api/rsvps/event/{event_id}", json={})

    assert response.status_code == 401
    assert response.json()["error"] == "Authentication required for this event"


def test_rsvp_to_missing_event_returns_404():
    response = requests.post(f"{BASE_URL}/api/rsvps/event/999999999", json={})

    assert response.status_code == 404
