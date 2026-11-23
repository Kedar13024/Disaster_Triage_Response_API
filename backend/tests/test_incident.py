import json


def test_create_incident(client, user_payload ):
    # 1. Register a user
    register_response = client.post("/users", json=user_payload)
    assert register_response.status_code == 201

    # 2. Login to obtain an access token
    login_response = client.post(
        "/login",
        data={
            "username": user_payload["user_email"],
            "password": user_payload["user_password"],
        },
    )
    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    # 3. Use the token to access the protected endpoint
    headers = {"Authorization": f"Bearer {token}"}

    # 4. Create an incident
    incident_payload = {
        "incident_category": "natural_disaster",
        "incident_type": "flood",
        "description": "Severe flooding has affected several homes.",
    }

    response = client.post(
        "/incidents/",
        json=incident_payload,
        headers=headers,
    )

    # 5. Verify the response
    assert response.status_code == 201

    data = response.json()

    assert data["incident_category"] == "natural_disaster"
    assert data["incident_type"] == "flood"
    assert data["description"] == incident_payload["description"]
    assert data["incident_id"] is not None
    assert data["reported_by"] == register_response.json()["user_id"]
    assert "reported_at" in data

def test_get_incident(client, user_payload):

    # Register
    register_response = client.post("/users", json=user_payload)
    assert register_response.status_code == 201

    # Login
    login_response = client.post(
        "/login/",
        data={
            "username": user_payload["user_email"],
            "password": user_payload["user_password"],
        },
    )
    assert login_response.status_code == 200

    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create incident
    incident_payload = {
        "incident_category": "natural_disaster",
        "incident_type": "flood",
        "description": "Severe flooding has affected several homes.",
    }

    create_response = client.post(
        "/incidents/",
        json=incident_payload,
        headers=headers,
    )

    assert create_response.status_code == 201

    incident_id = create_response.json()["incident_id"]

    # Retrieve incident by ID
    response = client.get(
        f"/incidents/{incident_id}",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["incident_id"] == incident_id
    assert data["incident_type"] == "flood"
    assert data["incident_category"] == "natural_disaster"
    assert data["description"] == incident_payload["description"]


def test_get_non_existent_incident(client, user_payload):

    # Register
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
    headers = {"Authorization": f"Bearer {token}"}


    # Retrieve incident by ID
    response = client.get(
        "/incidents/999999",
        headers=headers,
    )

    assert response.status_code == 404

def test_update_incident(client, user_payload):
    # Register
    register_response = client.post("/users/", json=user_payload)
    assert register_response.status_code == 201

    # Login
    login_response = client.post(
        "/login/",
        data={
            "username": user_payload["user_email"],
            "password": user_payload["user_password"],
        },
    )
    assert login_response.status_code == 200

    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create incident
    incident_payload = {
        "incident_category": "natural_disaster",
        "incident_type": "flood",
        "description": "Severe flooding has affected several homes.",
    }

    create_response = client.post(
        "/incidents/",
        json=incident_payload,
        headers=headers,
    )
    assert create_response.status_code == 201

    incident_id = create_response.json()["incident_id"]

    # Update incident
    update_payload = {
        "description": "Updated report: flooding has affected several streets.",
    }

    response = client.patch(
        f"/incidents/{incident_id}",
        json=update_payload,
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()
    assert data["incident_id"] == incident_id
    assert data["description"] == update_payload["description"]
    assert data["incident_type"] == "flood"

def test_update_incident_by_non_owner(client, user_payload):
    # Register User A (owner)
    register_response = client.post("/users/", json=user_payload)
    assert register_response.status_code == 201

    # Login User A
    login_response = client.post(
        "/login/",
        data={
            "username": user_payload["user_email"],
            "password": user_payload["user_password"],
        },
    )
    assert login_response.status_code == 200

    owner_token = login_response.json()["access_token"]
    owner_headers = {"Authorization": f"Bearer {owner_token}"}

    # User A creates an incident
    incident_payload = {
        "incident_category": "natural_disaster",
        "incident_type": "flood",
        "description": "Severe flooding has affected several homes.",
    }

    create_response = client.post(
        "/incidents/",
        json=incident_payload,
        headers=owner_headers,
    )
    assert create_response.status_code == 201

    incident_id = create_response.json()["incident_id"]

    # Register User B (non-owner)
    second_user = user_payload.copy()
    second_user["user_email"] = "another_citizen@example.com"
    second_user["user_phoneno"] = "+919876543211"

    second_register_response = client.post(
        "/users/",
        json=second_user,
    )
    assert second_register_response.status_code == 201

    # Login User B
    second_login_response = client.post(
        "/login/",
        data={
            "username": second_user["user_email"],
            "password": second_user["user_password"],
        },
    )
    assert second_login_response.status_code == 200

    second_token = second_login_response.json()["access_token"]
    second_headers = {"Authorization": f"Bearer {second_token}"}

    # User B attempts to update User A's incident
    update_payload = {
        "description": "Unauthorized attempt to change this incident.",
    }

    response = client.patch(
        f"/incidents/{incident_id}",
        json=update_payload,
        headers=second_headers,
    )

    assert response.status_code == 403

def test_delete_incident(client, user_payload):
    # Register
    register_response = client.post("/users/", json=user_payload)
    assert register_response.status_code == 201

    # Login
    login_response = client.post(
        "/login/",
        data={
            "username": user_payload["user_email"],
            "password": user_payload["user_password"],
        },
    )
    assert login_response.status_code == 200

    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create incident
    incident_payload = {
        "incident_category": "natural_disaster",
        "incident_type": "flood",
        "description": "Severe flooding has affected several homes.",
    }

    create_response = client.post(
        "/incidents/",
        json=incident_payload,
        headers=headers,
    )
    assert create_response.status_code == 201

    incident_id = create_response.json()["incident_id"]

    # Delete incident
    response = client.delete(
        f"/incidents/{incident_id}",
        headers=headers,
    )

    assert response.status_code == 204

    # Verify the incident no longer exists
    get_response = client.get(
        f"/incidents/{incident_id}",
        headers=headers,
    )

    assert get_response.status_code == 404

def test_delete_incident_by_non_owner(client, user_payload):
    # Register User A (owner)
    register_response = client.post("/users/", json=user_payload)
    assert register_response.status_code == 201

    # Login User A
    login_response = client.post(
        "/login/",
        data={
            "username": user_payload["user_email"],
            "password": user_payload["user_password"],
        },
    )
    assert login_response.status_code == 200

    owner_token = login_response.json()["access_token"]
    owner_headers = {"Authorization": f"Bearer {owner_token}"}

    # User A creates an incident
    incident_payload = {
        "incident_category": "natural_disaster",
        "incident_type": "flood",
        "description": "Severe flooding has affected several homes.",
    }

    create_response = client.post(
        "/incidents/",
        json=incident_payload,
        headers=owner_headers,
    )
    assert create_response.status_code == 201

    incident_id = create_response.json()["incident_id"]

    # Register User B
    second_user = user_payload.copy()
    second_user["user_email"] = "another_citizen@example.com"
    second_user["user_phoneno"] = "+919876543211"

    second_register_response = client.post(
        "/users/",
        json=second_user,
    )
    assert second_register_response.status_code == 201

    # Login User B
    second_login_response = client.post(
        "/login/",
        data={
            "username": second_user["user_email"],
            "password": second_user["user_password"],
        },
    )
    assert second_login_response.status_code == 200

    second_token = second_login_response.json()["access_token"]
    second_headers = {"Authorization": f"Bearer {second_token}"}

    # User B attempts to delete User A's incident
    response = client.delete(
        f"/incidents/{incident_id}",
        headers=second_headers,
    )

    assert response.status_code == 403

    # Verify the incident still exists for its owner
    get_response = client.get(
        f"/incidents/{incident_id}",
        headers=owner_headers,
    )

    assert get_response.status_code == 200

def test_update_incident_empty_payload(client, user_payload):
    # Register
    register_response = client.post("/users/", json=user_payload)
    assert register_response.status_code == 201

    # Login
    login_response = client.post(
        "/login/",
        data={
            "username": user_payload["user_email"],
            "password": user_payload["user_password"],
        },
    )
    assert login_response.status_code == 200

    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create incident
    incident_payload = {
        "incident_category": "natural_disaster",
        "incident_type": "flood",
        "description": "Severe flooding has affected several homes.",
    }

    create_response = client.post(
        "/incidents/",
        json=incident_payload,
        headers=headers,
    )
    assert create_response.status_code == 201

    incident_id = create_response.json()["incident_id"]

    # Attempt update with an empty payload
    response = client.patch(
        f"/incidents/{incident_id}",
        json={},
        headers=headers,
    )

    assert response.status_code == 400

def test_update_nonexistent_incident(client, user_payload):
    # Register
    register_response = client.post("/users/", json=user_payload)
    assert register_response.status_code == 201

    # Login
    login_response = client.post(
        "/login/",
        data={
            "username": user_payload["user_email"],
            "password": user_payload["user_password"],
        },
    )
    assert login_response.status_code == 200

    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Attempt to update an incident that doesn't exist
    response = client.patch(
        "/incidents/999999",
        json={"description": "This incident does not exist."},
        headers=headers,
    )

    assert response.status_code == 404

def test_delete_nonexistent_incident(client, user_payload):
    # Register
    register_response = client.post("/users/", json=user_payload)
    assert register_response.status_code == 201

    # Login
    login_response = client.post(
        "/login/",
        data={
            "username": user_payload["user_email"],
            "password": user_payload["user_password"],
        },
    )
    assert login_response.status_code == 200

    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Attempt to delete a nonexistent incident
    response = client.delete(
        "/incidents/999999",
        headers=headers,
    )

    assert response.status_code == 404