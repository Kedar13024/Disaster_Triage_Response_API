"""Routes for creating, viewing, updating, and deleting incidents."""


from fastapi import Depends, HTTPException, Query, Response, status , APIRouter
from backend.core.oauth2 import get_current_user
from backend.models import models
from backend.database.database import get_db , Session
from backend.schemas.incident_sch import IncidentCreate , IncidentResponse , IncidentUpdate
from backend.schemas.user_sch import UserRole


router = APIRouter(prefix="/incidents" , tags=["Incidents"])


@router.get("/", response_model=list[IncidentResponse])
def get_incidents(
    db : Session = Depends(get_db) ,
    limit : int = Query(20,ge=1,le=100),
    skip : int = Query(0 , ge=0)
    ):
    """Return paginated published incidents."""
    
    incidents = (
    db.query(models.Incident).filter(models.Incident.published.is_(True))
    .order_by(models.Incident.reported_at.desc() , models.Incident.incident_id.desc())
    .limit(limit)
    .offset(skip)
    .all()
    )

    return incidents

@router.get("/my", response_model=list[IncidentResponse])
def get_my_incidents(
    db : Session = Depends(get_db) ,
    limit : int = Query(20,ge=1,le=100),
    skip : int = Query(0 , ge=0),
    current_user : models.User = Depends(get_current_user)
    ):
    """Return paginated incidents reported by current user."""
    
    incidents = (
    db.query( models.Incident).filter(models.Incident.reported_by == current_user.user_id)
    .order_by(models.Incident.reported_at.desc() , models.Incident.incident_id.desc())
    .limit(limit)
    .offset(skip)
    .all()
    )

    return incidents


@router.get("/{incident_id}", response_model=IncidentResponse)
def get_incident(incident_id: int , db : Session = Depends(get_db) , current_user : models.User = Depends(get_current_user)):
    """Return a published incident by ID or raise 404 if it is unavailable."""

    matched_incident = (
        db.query(models.Incident)
        .filter(
            models.Incident.incident_id == incident_id ,
        ).first()
    )

    if matched_incident is None :
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Published incident {incident_id} was not found.",
        )

    is_owner = matched_incident.reported_by == current_user.user_id
    is_admin = current_user.user_role == UserRole.ADMIN


    if matched_incident:
        if not matched_incident.published and not is_owner and not is_admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Published incident {incident_id} was not found.",
            )

    return matched_incident


@router.post("/",response_model=IncidentResponse,status_code=status.HTTP_201_CREATED )
def create_incident(incident: IncidentCreate , db : Session = Depends(get_db),  current_user : models.User = Depends(get_current_user)):
    """Create an incident attributed to the authenticated user."""
    new_incident = models.Incident(reported_by=current_user.user_id,**incident.model_dump())
    db.add(new_incident)
    db.commit()
    db.refresh(new_incident)
    return new_incident


@router.patch("/{incident_id}", response_model=IncidentResponse )
def update_incident(incident_id: int, incident: IncidentUpdate , db : Session = Depends(get_db) , current_user : models.User = Depends(get_current_user)):
    """Apply supplied changes to an incident owned by the authenticated user."""

    old_incident = db.query(models.Incident).filter(
        models.Incident.incident_id == incident_id
    ).first()


    if old_incident is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident {incident_id} was not found.",
        )

    is_owner = old_incident.reported_by == current_user.user_id
    is_admin = current_user.user_role == UserRole.ADMIN
    
    if not is_owner and not is_admin :
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN , detail= "You do not have permission to update this incident."
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



@router.delete("/{incident_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_incident(incident_id: int , db : Session = Depends(get_db), current_user : models.User = Depends(get_current_user)):
    """Delete a incident when the user owns it or is an administrator."""
    incident = db.query(models.Incident).filter(
        models.Incident.incident_id == incident_id,
    ).first()

    if incident is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident {incident_id} was not found.",
        )

    is_owner = incident.reported_by == current_user.user_id
    is_admin = current_user.user_role == UserRole.ADMIN

    if not is_owner and not is_admin :
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN , detail= "You do not have permission to delete this incident."
        )

    db.delete(incident)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
