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


class IncidentUpdate(IncidentBase):
    """Fields needed to update an incident."""

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
    return incidents

@app.get("/incidents/{incident_id}", response_model=IncidentResponse, tags=["Incidents"])
def get_incident(incident_id: int , db : Session = Depends(get_db)):
    """Return one incident by its ID."""
    matched_incident = db.query(models.Incident).filter(models.Incident.incident_id == incident_id,models.Incident.published.is_(True)).first()
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


@app.put("/incidents/{incident_id}", response_model=IncidentResponse, tags=["Incidents"])
def update_incident(incident_id: int, incident: IncidentUpdate , db : Session = Depends(get_db)):
    """Replace the details of an existing incident."""
    matched_incident_query = db.query(models.Incident).filter(models.Incident.incident_id == incident_id)
    old_incident = matched_incident_query.first()
    updated_incident = incident.model_dump()
    matched_incident_query.update(
        updated_incident,  synchronize_session=False
    )
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
    db.delete(
        db.query(models.Incident).filter(models.Incident.incident_id == incident_id , models.Incident.published.is_(True)).first()
    )
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
