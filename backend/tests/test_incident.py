from datetime import datetime
from backend.models import models


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


def test_incident_pagination_limit(client, user_payload):
    # Register user
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

    # Create 3 incidents
    for i in range(3):
        incident_payload = {
            "incident_category": "natural_disaster",
            "incident_type": "flood",
            "description": f"Flooding incident report number {i}.",
        }

        create_response = client.post(
            "/incidents/",
            json=incident_payload,
            headers=headers,
        )

        assert create_response.status_code == 201

    # Request only 2 incidents
    response = client.get("/incidents?limit=2")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_incident_pagination_offset(client, user_payload):
    # Register user
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

    # Create 3 incidents
    for i in range(3):
        incident_payload = {
            "incident_category": "natural_disaster",
            "incident_type": "flood",
            "description": f"Flooding incident report number {i}.",
        }

        create_response = client.post(
            "/incidents",
            json=incident_payload,
            headers=headers,
        )

        assert create_response.status_code == 201

    # Request incidents after skipping the first one
    response = client.get("/incidents?skip=1&limit=2")

    assert response.status_code == 200
    assert len(response.json()) == 2

def test_incident_invalid_pagination(client):
    # limit cannot be zero
    response = client.get("/incidents?limit=0")
    assert response.status_code == 422

    # limit cannot exceed 100
    response = client.get("/incidents?limit=101")
    assert response.status_code == 422

    # skip cannot be negative
    response = client.get("/incidents?skip=-1")
    assert response.status_code == 422

def test_incident_filter_by_severity(client, db_session, user_payload):
    # Register user
    register_response = client.post("/users/", json=user_payload)
    assert register_response.status_code == 201

    user_id = register_response.json()["user_id"]

    # Insert incidents directly into the test database
    incidents = [
        models.Incident(
            incident_category="natural_disaster",
            incident_type="flood",
            description="High severity flooding incident report.",
            severity="high",
            reported_by=user_id,
        ),
        models.Incident(
            incident_category="natural_disaster",
            incident_type="flood",
            description="Low severity flooding incident report.",
            severity="low",
            reported_by=user_id,
        ),
        models.Incident(
            incident_category="natural_disaster",
            incident_type="flood",
            description="Another high severity flooding incident report.",
            severity="high",
            reported_by=user_id,
        ),
    ]

    db_session.add_all(incidents)
    db_session.commit()

    # Request only high-severity incidents
    response = client.get("/incidents/?severity=high")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert all(
        incident["severity"] == "high"
        for incident in data
    )

def test_incident_filter_by_category(client, user_payload):
    # Register user
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

    # Create incidents with different categories
    categories = [
        "natural_disaster",
        "human_caused",
        "natural_disaster",
    ]

    for i, category in enumerate(categories):
        incident_payload = {
            "incident_category": category,
            "incident_type": "flood",
            "description": f"Incident report number {i} with sufficient details.",
        }

        create_response = client.post(
            "/incidents/",
            json=incident_payload,
            headers=headers,
        )

        assert create_response.status_code == 201

    # Request only natural disaster incidents
    response = client.get(
        "/incidents/?incident_category=natural_disaster"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert all(
        incident["incident_category"] == "natural_disaster"
        for incident in data
    )

def test_incident_filter_by_type(client, user_payload):
    # Register user
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

    # Create incidents with different types
    incident_types = ["flood", "earthquake", "flood"]

    for i, incident_type in enumerate(incident_types):
        incident_payload = {
            "incident_category": "natural_disaster",
            "incident_type": incident_type,
            "description": f"Incident report number {i} with sufficient details.",
        }

        create_response = client.post(
            "/incidents/",
            json=incident_payload,
            headers=headers,
        )

        assert create_response.status_code == 201

    # Request only flood incidents
    response = client.get("/incidents/?incident_type=flood")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert all(
        incident["incident_type"] == "flood"
        for incident in data
    )

def test_incident_search(client, user_payload):
    # Register user
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

    # Create incidents with different descriptions
    descriptions = [
        "Severe flooding has affected several homes.",
        "A major earthquake damaged several buildings.",
        "Flood waters have damaged several roads.",
    ]

    for description in descriptions:
        incident_payload = {
            "incident_category": "natural_disaster",
            "incident_type": "flood",
            "description": description,
        }

        create_response = client.post(
            "/incidents/",
            json=incident_payload,
            headers=headers,
        )

        assert create_response.status_code == 201

    # Search for flooding
    response = client.get("/incidents/?search=flood")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert all(
        "flood" in incident["description"].lower()
        for incident in data
    )

def test_incident_search_case_insensitive(client, user_payload):
    # Register user
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

    # Search using uppercase letters
    response = client.get("/incidents/?search=FLOOD")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert "flood" in data[0]["description"].lower()

def test_incident_search_with_whitespace(client, user_payload):
    # Register user
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

    # Search with spaces around the word
    response = client.get("/incidents/?search=%20flood%20")

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 1
    assert "flood" in data[0]["description"].lower()

def test_incident_filter_by_start_date(client, db_session, user_payload):
    # Register user
    register_response = client.post("/users/", json=user_payload)
    assert register_response.status_code == 201

    user_id = register_response.json()["user_id"]

    # Create incidents with fixed reported dates
    incidents = [
        models.Incident(
            incident_category="natural_disaster",
            incident_type="flood",
            description="Older flooding incident report.",
            severity="low",
            reported_by=user_id,
            reported_at=datetime(2025, 1, 5, 10, 0, 0),
            published=True,
        ),
        models.Incident(
            incident_category="natural_disaster",
            incident_type="flood",
            description="January 10 flooding incident report.",
            severity="medium",
            reported_by=user_id,
            reported_at=datetime(2025, 1, 10, 10, 0, 0),
            published=True,
        ),
        models.Incident(
            incident_category="natural_disaster",
            incident_type="flood",
            description="January 15 flooding incident report.",
            severity="high",
            reported_by=user_id,
            reported_at=datetime(2025, 1, 15, 10, 0, 0),
            published=True,
        ),
    ]

    db_session.add_all(incidents)
    db_session.commit()

    # Search from January 10 onwards
    response = client.get(
        "/incidents/?start_date=2025-01-10T00:00:00"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert all(
        incident["reported_at"] >= "2025-01-10"
        for incident in data
    )

def test_incident_filter_by_end_date(client, db_session, user_payload):
    # Register user
    register_response = client.post("/users/", json=user_payload)
    assert register_response.status_code == 201

    user_id = register_response.json()["user_id"]

    incidents = [
        models.Incident(
            incident_category="natural_disaster",
            incident_type="flood",
            description="January 5 flooding incident report.",
            severity="low",
            reported_by=user_id,
            reported_at=datetime(2025, 1, 5, 10, 0, 0),
            published=True,
        ),
        models.Incident(
            incident_category="natural_disaster",
            incident_type="flood",
            description="January 10 flooding incident report.",
            severity="medium",
            reported_by=user_id,
            reported_at=datetime(2025, 1, 10, 10, 0, 0),
            published=True,
        ),
        models.Incident(
            incident_category="natural_disaster",
            incident_type="flood",
            description="January 15 flooding incident report.",
            severity="high",
            reported_by=user_id,
            reported_at=datetime(2025, 1, 15, 10, 0, 0),
            published=True,
        ),
    ]

    db_session.add_all(incidents)
    db_session.commit()

    # Search up to January 10
    response = client.get(
        "/incidents/?end_date=2025-01-10T23:59:59"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert all(
        incident["reported_at"] <= "2025-01-10T23:59:59"
        for incident in data
    )

def test_incident_filter_by_date_range(client, db_session, user_payload):
    register_response = client.post("/users/", json=user_payload)
    assert register_response.status_code == 201

    user_id = register_response.json()["user_id"]

    incidents = [
        models.Incident(
            incident_category="natural_disaster",
            incident_type="flood",
            description="January 5 flooding incident report.",
            severity="low",
            reported_by=user_id,
            reported_at=datetime(2025, 1, 5, 10, 0, 0),
            published=True,
        ),
        models.Incident(
            incident_category="natural_disaster",
            incident_type="flood",
            description="January 10 flooding incident report.",
            severity="medium",
            reported_by=user_id,
            reported_at=datetime(2025, 1, 10, 10, 0, 0),
            published=True,
        ),
        models.Incident(
            incident_category="natural_disaster",
            incident_type="flood",
            description="January 15 flooding incident report.",
            severity="high",
            reported_by=user_id,
            reported_at=datetime(2025, 1, 15, 10, 0, 0),
            published=True,
        ),
    ]

    db_session.add_all(incidents)
    db_session.commit()

    response = client.get(
        "/incidents/?start_date=2025-01-08T00:00:00"
        "&end_date=2025-01-12T23:59:59"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert "January 10" in data[0]["description"]

def test_incident_invalid_date_range(client):
    response = client.get(
        "/incidents/?start_date=2025-01-15T00:00:00"
        "&end_date=2025-01-10T00:00:00"
    )

    assert response.status_code == 422
    assert response.json()["detail"] == (
        "start_date must be earlier than or equal to end_date."
    )

def test_incident_sort_newest_first(client, db_session, user_payload):
    register_response = client.post("/users/", json=user_payload)
    assert register_response.status_code == 201

    user_id = register_response.json()["user_id"]

    incidents = [
        models.Incident(
            incident_category="natural_disaster",
            incident_type="flood",
            description="Oldest incident.",
            severity="low",
            reported_by=user_id,
            reported_at=datetime(2025, 1, 5, 10, 0, 0),
            published=True,
        ),
        models.Incident(
            incident_category="natural_disaster",
            incident_type="flood",
            description="Newest incident.",
            severity="high",
            reported_by=user_id,
            reported_at=datetime(2025, 1, 15, 10, 0, 0),
            published=True,
        ),
        models.Incident(
            incident_category="natural_disaster",
            incident_type="flood",
            description="Middle incident.",
            severity="medium",
            reported_by=user_id,
            reported_at=datetime(2025, 1, 10, 10, 0, 0),
            published=True,
        ),
    ]

    db_session.add_all(incidents)
    db_session.commit()

    response = client.get("/incidents/?sort_by=newest")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 3
    assert data[0]["description"] == "Newest incident."
    assert data[1]["description"] == "Middle incident."
    assert data[2]["description"] == "Oldest incident."

def test_incident_sort_oldest_first(client, db_session, user_payload):
    register_response = client.post("/users/", json=user_payload)
    assert register_response.status_code == 201

    user_id = register_response.json()["user_id"]

    incidents = [
        models.Incident(
            incident_category="natural_disaster",
            incident_type="flood",
            description="Oldest incident.",
            severity="low",
            reported_by=user_id,
            reported_at=datetime(2025, 1, 5, 10, 0, 0),
            published=True,
        ),
        models.Incident(
            incident_category="natural_disaster",
            incident_type="flood",
            description="Newest incident.",
            severity="high",
            reported_by=user_id,
            reported_at=datetime(2025, 1, 15, 10, 0, 0),
            published=True,
        ),
        models.Incident(
            incident_category="natural_disaster",
            incident_type="flood",
            description="Middle incident.",
            severity="medium",
            reported_by=user_id,
            reported_at=datetime(2025, 1, 10, 10, 0, 0),
            published=True,
        ),
    ]

    db_session.add_all(incidents)
    db_session.commit()

    response = client.get("/incidents/?sort_by=oldest")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 3
    assert data[0]["description"] == "Oldest incident."
    assert data[1]["description"] == "Middle incident."
    assert data[2]["description"] == "Newest incident."

def test_incident_sort_by_severity(client, db_session, user_payload):
    register_response = client.post("/users/", json=user_payload)
    assert register_response.status_code == 201

    user_id = register_response.json()["user_id"]

    incidents = [
        models.Incident(
            incident_category="natural_disaster",
            incident_type="flood",
            description="Low severity incident.",
            severity="low",
            reported_by=user_id,
            reported_at=datetime(2025, 1, 15, 10, 0, 0),
            published=True,
        ),
        models.Incident(
            incident_category="natural_disaster",
            incident_type="flood",
            description="Critical severity incident.",
            severity="critical",
            reported_by=user_id,
            reported_at=datetime(2025, 1, 5, 10, 0, 0),
            published=True,
        ),
        models.Incident(
            incident_category="natural_disaster",
            incident_type="flood",
            description="Medium severity incident.",
            severity="medium",
            reported_by=user_id,
            reported_at=datetime(2025, 1, 10, 10, 0, 0),
            published=True,
        ),
        models.Incident(
            incident_category="natural_disaster",
            incident_type="flood",
            description="High severity incident.",
            severity="high",
            reported_by=user_id,
            reported_at=datetime(2025, 1, 12, 10, 0, 0),
            published=True,
        ),
    ]

    db_session.add_all(incidents)
    db_session.commit()

    response = client.get("/incidents/?sort_by=severity")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 4

    expected_order = [
        "critical",
        "high",
        "medium",
        "low",
    ]

    actual_order = [
        incident["severity"] for incident in data
    ]

    assert actual_order == expected_order

def test_incident_search_only_whitespace(client):
    response = client.get("/incidents/?search=%20%20%20")

    assert response.status_code == 422
    assert response.json()["detail"] == (
        "Search cannot contain only whitespace."
    )

def test_incident_search_exceeds_max_length(client):
    long_search = "a" * 201

    response = client.get(
        f"/incidents/?search={long_search}"
    )

    assert response.status_code == 422

def test_incident_invalid_severity(client):
    response = client.get("/incidents/?severity=urgent")

    assert response.status_code == 422

def test_incident_invalid_sort_option(client):
    response = client.get("/incidents/?sort_by=popular")

    assert response.status_code == 422

def test_incident_invalid_category(client):
    response = client.get(
        "/incidents/?incident_category=invalid_category"
    )

    assert response.status_code == 422

def test_incident_invalid_type(client):
    response = client.get(
        "/incidents/?incident_type=invalid_type"
    )

    assert response.status_code == 422

def test_unpublished_incident_not_in_public_feed(
    client, db_session, user_payload
):
    register_response = client.post("/users/", json=user_payload)
    assert register_response.status_code == 201

    user_id = register_response.json()["user_id"]

    incidents = [
        models.Incident(
            incident_category="natural_disaster",
            incident_type="flood",
            description="Published flooding incident.",
            severity="high",
            reported_by=user_id,
            published=True,
        ),
        models.Incident(
            incident_category="natural_disaster",
            incident_type="flood",
            description="Unpublished flooding incident.",
            severity="high",
            reported_by=user_id,
            published=False,
        ),
    ]

    db_session.add_all(incidents)
    db_session.commit()

    response = client.get("/incidents/")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["description"] == "Published flooding incident."
    assert all(incident["published"] for incident in data)

def test_owner_can_view_unpublished_incident(
    client, db_session, user_payload
):
    # Register user
    register_response = client.post("/users/", json=user_payload)
    assert register_response.status_code == 201

    user_id = register_response.json()["user_id"]

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

    # Insert unpublished incident
    incident = models.Incident(
        incident_category="natural_disaster",
        incident_type="flood",
        description="My unpublished flooding incident.",
        severity="high",
        reported_by=user_id,
        published=False,
    )

    db_session.add(incident)
    db_session.commit()
    db_session.refresh(incident)

    # Owner requests their incident
    response = client.get(
        f"/incidents/{incident.incident_id}",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["published"] is False
    assert response.json()["description"] == (
        "My unpublished flooding incident."
    )

def test_non_owner_cannot_view_unpublished_incident(
    client, db_session, user_payload
):
    # Register owner
    owner_response = client.post("/users/", json=user_payload)
    assert owner_response.status_code == 201

    owner_id = owner_response.json()["user_id"]

    # Register another user
    other_user_payload = user_payload.copy()
    other_user_payload["user_email"] = "another@example.com"
    other_user_payload["user_phoneno"] = "+919876543211"

    other_response = client.post(
        "/users/", json=other_user_payload
    )
    assert other_response.status_code == 201

    # Login as the other user
    login_response = client.post(
        "/login/",
        data={
            "username": other_user_payload["user_email"],
            "password": other_user_payload["user_password"],
        },
    )
    assert login_response.status_code == 200

    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create unpublished incident belonging to owner
    incident = models.Incident(
        incident_category="natural_disaster",
        incident_type="flood",
        description="Private unpublished flooding incident.",
        severity="high",
        reported_by=owner_id,
        published=False,
    )

    db_session.add(incident)
    db_session.commit()
    db_session.refresh(incident)

    # Other user attempts to access it
    response = client.get(
        f"/incidents/{incident.incident_id}",
        headers=headers,
    )

    assert response.status_code == 404

def test_pagination_excludes_unpublished_incidents(
    client, db_session, user_payload
):
    register_response = client.post("/users/", json=user_payload)
    assert register_response.status_code == 201

    user_id = register_response.json()["user_id"]

    incidents = [
        models.Incident(
            incident_category="natural_disaster",
            incident_type="flood",
            description="Published incident one.",
            severity="low",
            reported_by=user_id,
            published=True,
        ),
        models.Incident(
            incident_category="natural_disaster",
            incident_type="flood",
            description="Unpublished incident.",
            severity="high",
            reported_by=user_id,
            published=False,
        ),
        models.Incident(
            incident_category="natural_disaster",
            incident_type="flood",
            description="Published incident two.",
            severity="medium",
            reported_by=user_id,
            published=True,
        ),
    ]

    db_session.add_all(incidents)
    db_session.commit()

    response = client.get("/incidents/?limit=10&skip=0")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert all(incident["published"] for incident in data)