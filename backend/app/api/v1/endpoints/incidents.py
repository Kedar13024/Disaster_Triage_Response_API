from fastapi import Depends, HTTPException, Response, status , APIRouter
from backend.models import models
from backend.database.database import get_db , Session
from backend.schemas.incident_sch import IncidentCreate , IncidentResponse , IncidentUpdate


router = APIRouter(prefix="/incidents" , tags=["Incidents"])


@router.get("/", response_model=list[IncidentResponse])
def get_incidents(db : Session = Depends(get_db)):
    """Return all incidents."""
    
    incidents = db.query(models.Incident).filter(models.Incident.published.is_(True)).all()

    if not incidents:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No published incidents were found.",
        )

    return incidents

@router.get("/{incident_id}", response_model=IncidentResponse)
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


@router.post("/",response_model=IncidentResponse,status_code=status.HTTP_201_CREATED)
def create_incident(incident: IncidentCreate , db : Session = Depends(get_db)):
    """Add a new incident and assign it the next available ID."""
    new_incident = models.Incident(**incident.model_dump())
    db.add(new_incident)
    db.commit()
    db.refresh(new_incident)
    return new_incident


@router.patch("/{incident_id}", response_model=IncidentResponse)
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



@router.delete("/{incident_id}", status_code=status.HTTP_204_NO_CONTENT,)
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
