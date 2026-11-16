from fastapi import Depends, FastAPI, HTTPException, Response, status
from backend.models import models
from backend.database.database import engine, get_db , Session
from backend.schemas.incident_sch import IncidentCreate , IncidentResponse , IncidentUpdate
from backend.schemas.user_sch import User, User_response
from backend.security.security import hashed_pass

app = FastAPI(title="Disaster Triage Response API")


models.Base.metadata.create_all(bind=engine)



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


@app.post(
    "/users",
    response_model=User_response,
    status_code=status.HTTP_201_CREATED,
    tags=["Users"],
)
def create_user(user: User, db: Session = Depends(get_db)):
    """Register a user with a securely hashed password."""
    existing_user = (
        db.query(models.User)
        .filter(models.User.user_email == str(user.user_email))
        .first()
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    new_user = models.User(
        user_fullname=user.user_fullname,
        user_phoneno=str(user.user_phoneno),
        user_email=str(user.user_email),
        user_password=hashed_pass(user.user_password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


