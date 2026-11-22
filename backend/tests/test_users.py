# tests/test_users.py

def test_create_user(client , user_payload):

    response = client.post("/users", json=user_payload)

    assert response.status_code == 201

    data = response.json()

    assert data["user_email"] == user_payload["user_email"]
    assert data["user_role"] == "citizen"
    assert "user_id" in data
    assert "created_at" in data
    assert "user_password" not in data

def test_duplicate_user_registration(client , user_payload):

    first_response = client.post("/users", json=user_payload)

    assert first_response.status_code == 201

    second_response = client.post("/users", json=user_payload)

    assert second_response.status_code == 409
    assert second_response.json()["detail"] == (
        "An account with this email already exists."
    )

def test_registration_invalid_email(client, user_payload):

    payload = user_payload.copy()
    payload["user_email"] = "not-an-email"

    response = client.post("/users", json=payload)

    assert response.status_code == 422