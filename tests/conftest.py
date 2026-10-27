import os
import time

import pytest
import requests

BASE_URL = os.environ.get("BASE_URL", "http://localhost:5000")


def unique_username(prefix="user"):
    return f"{prefix}_{time.time_ns()}"


@pytest.fixture
def user_credentials():
    """Registers a fresh user and returns its username and password."""
    creds = {"username": unique_username(), "password": "secret123"}
    response = requests.post(f"{BASE_URL}/api/auth/register", json=creds)
    assert response.status_code == 201
    return creds


@pytest.fixture
def auth_token(user_credentials):
    """Logs the fresh user in and returns a valid JWT."""
    response = requests.post(f"{BASE_URL}/api/auth/login", json=user_credentials)
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}
