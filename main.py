from datetime import datetime
from fastapi import Depends, FastAPI, HTTPException, Response, status
from pydantic import BaseModel, ConfigDict
from backend.models import models
from backend.database.database import engine, get_db , Session

app = FastAPI(title="Disaster Triage Response API")


models.Base.metadata.create_all(bind=engine)

class IncidentBase(BaseModel):
    """An incident returned by the API."""

    incident_type: str
    description: str
    severity : str
    published : bool


class IncidentCreate(IncidentBase):
    """Fields needed to report  an incident."""


class IncidentUpdate(BaseModel):
    """Fields needed to update an incident."""
    incident_type: str | None
    description: str | None
    severity : str | None
    published : bool | None

class IncidentResponse(IncidentBase):
    """Serialize an incident"""

    model_config = ConfigDict(from_attributes=True)

    incident_id: int
    reported_at: datetime


@app.get("/home", tags=["Getting started"])
def home():
    return {"message": "Welcome to the Disaster Triage Response API"}


@app.get("/incidents", response_model=list[IncidentResponse], tags=["Incidents"])
def get_incidents(db : Session = Depends(get_db)):
    """Return all incidents."""
    
    incidents = db.query(models.Incident).filter(models.Incident.published.is_(True)).all()

    if not incidents:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No published incidents were found.",
        )

    return incidents

@app.get("/incidents/{incident_id}", response_model=IncidentResponse, tags=["Incidents"])
def get_incident(incident_id: int , db : Session = Depends(get_db)):
    """Return one incident by its ID."""

    matched_incident = (
        db.query(models.Incident)
        .filter(
            models.Incident.incident_id == incident_id,
            models.Incident.published.is_(True),
        )
        .first()
    )

    if matched_incident is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Published incident {incident_id} was not found.",
        )

    return matched_incident


@app.post(
    "/incidents",
    response_model=IncidentResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Incidents"],
)
def create_incident(incident: IncidentCreate , db : Session = Depends(get_db)):
    """Add a new incident and assign it the next available ID."""
    new_incident = models.Incident(**incident.model_dump())
    db.add(new_incident)
    db.commit()
    db.refresh(new_incident)
    return new_incident


@app.patch("/incidents/{incident_id}", response_model=IncidentResponse, tags=["Incidents"])
def update_incident(incident_id: int, incident: IncidentUpdate , db : Session = Depends(get_db)):
    """Update the provided fields of an existing incident."""

    old_incident = db.query(models.Incident).filter(
        models.Incident.incident_id == incident_id
    ).first()


    if old_incident is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident {incident_id} was not found.",
        )

    updated_fields = incident.model_dump(exclude_unset=True)

    if not updated_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide at least one field to update.",
        )

    for field, value in updated_fields.items():
        setattr(old_incident, field, value)
    
    db.commit()
    db.refresh(old_incident)
    return old_incident



@app.delete(
    "/incidents/{incident_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Incidents"],
)
def delete_incident(incident_id: int , db : Session = Depends(get_db)):
    """Delete an incident."""
    incident = db.query(models.Incident).filter(
        models.Incident.incident_id == incident_id,
        models.Incident.published.is_(True),
    ).first()

    if incident is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Published incident {incident_id} was not found.",
        )

    db.delete(incident)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
