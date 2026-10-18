from datetime import datetime

from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel

app = FastAPI(title="Disaster Triage Response API")


class Incident(BaseModel):
    """An incident returned by the API."""

    incident_id: int
    incident_type: str
    incident_des: str
    reported_at: datetime


class IncidentCreate(BaseModel):
    """Fields needed to report or update an incident."""

    incident_type: str
    incident_des: str
    reported_at: datetime


# Simple in-memory sample data. It resets when the server restarts.
incidents: list[dict] = [
    {
        "incident_id": 1,
        "incident_type": "Flood",
        "incident_des": "Rising water reported near the east bridge.",
        "reported_at": datetime(2026, 10, 18, 8, 15),
    },
    {
        "incident_id": 2,
        "incident_type": "Wildfire",
        "incident_des": "Smoke reported near the northern forest road.",
        "reported_at": datetime(2026, 10, 18, 9, 30),
    },
    {
        "incident_id": 3,
        "incident_type": "Earthquake",
        "incident_des": "Residents reported shaking in the city center.",
        "reported_at": datetime(2026, 10, 18, 10, 5),
    },
    {
        "incident_id": 4,
        "incident_type": "Power outage",
        "incident_des": "Power is out across several streets in the west district.",
        "reported_at": datetime(2026, 10, 18, 11, 45),
    },
    {
        "incident_id": 5,
        "incident_type": "Landslide",
        "incident_des": "Debris has blocked part of the mountain highway.",
        "reported_at": datetime(2026, 10, 18, 13, 20),
    },
]


def find_incident(incident_id: int) -> dict:
    """Find an incident or return a clear 404 error."""
    for incident in incidents:
        if incident["incident_id"] == incident_id:
            return incident
    raise HTTPException(status_code=404, detail="Incident not found")


@app.get("/home", tags=["Getting started"])
def home():
    return {"message": "Welcome to the Disaster Triage Response API"}


@app.get("/incidents", response_model=list[Incident], tags=["Incidents"])
def get_incidents():
    """Return all incidents."""
    return incidents


@app.get("/incidents/{incident_id}", response_model=Incident, tags=["Incidents"])
def get_incident(incident_id: int):
    """Return one incident by its ID."""
    return find_incident(incident_id)


@app.post(
    "/incidents",
    response_model=Incident,
    status_code=status.HTTP_201_CREATED,
    tags=["Incidents"],
)
def create_incident(incident: IncidentCreate):
    """Add a new incident and assign it the next available ID."""
    new_id = max((item["incident_id"] for item in incidents), default=0) + 1
    new_incident = {"incident_id": new_id, **incident.model_dump()}
    incidents.append(new_incident)
    return new_incident


@app.put("/incidents/{incident_id}", response_model=Incident, tags=["Incidents"])
def update_incident(incident_id: int, incident: IncidentCreate):
    """Replace the details of an existing incident."""
    old_incident = find_incident(incident_id)
    updated_incident = {"incident_id": incident_id, **incident.model_dump()}
    incidents[incidents.index(old_incident)] = updated_incident
    return updated_incident


@app.delete(
    "/incidents/{incident_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Incidents"],
)
def delete_incident(incident_id: int):
    """Delete an incident."""
    incident = find_incident(incident_id)
    incidents.remove(incident)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
