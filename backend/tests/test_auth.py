"""Tests for login and authenticated endpoint access."""


def test_login_success(client, user_payload):
    """Verify valid credentials return a bearer token and the user's role."""

    # Register a user first
    register_response = client.post("/users", json=user_payload)

    assert register_response.status_code == 201

    # Login using the registered credentials
    response = client.post(
        "/login",
        data={
            "username": user_payload["user_email"],
            "password": user_payload["user_password"],
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["role"] == "citizen"
    assert data["access_token"] != ""

def test_login_wrong_password(client, user_payload):
    """Verify login rejects an incorrect password."""

    # Register user
    register_response = client.post("/users", json=user_payload)

    assert register_response.status_code == 201

    # Attempt login using wrong password
    response = client.post(
        "/login",
        data={
            "username": user_payload["user_email"],
            "password": "WrongPassword123!",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials!"


def test_login_wrong_email(client, user_payload):
    """Verify login rejects an email that is not registered."""

    # Register user
    register_response = client.post("/users", json=user_payload)

    assert register_response.status_code == 201

    # Attempt login using wrong email
    response = client.post(
        "/login",
        data={
            "username": "Wrong@example",
            "password": user_payload["user_password"],
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials!"


def test_access_protected_endpoint_without_token(client):
    """Verify protected incident endpoints reject requests without a token."""

    response = client.get("/incidents/my")

    assert response.status_code == 401

def test_access_protected_endpoint_with_token(client, user_payload):
    """Verify a valid bearer token grants access to the user's incident list."""

    # Register user
    register_response = client.post("/users", json=user_payload)

    assert register_response.status_code == 201

    # Login
    login_response = client.post(
        "/login",
        data={
            "username": user_payload["user_email"],
            "password": user_payload["user_password"],
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    # Access protected endpoint using token
    response = client.get(
        "/incidents/my",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200
    assert response.json() == []
