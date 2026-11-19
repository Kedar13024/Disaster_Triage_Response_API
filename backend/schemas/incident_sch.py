"""Pydantic request and response schemas for incident endpoints."""

from pydantic import BaseModel, ConfigDict
from datetime import datetime

from backend.schemas.user_sch import User_response

class IncidentBase(BaseModel):
    """An incident returned by the API."""

    incident_type: str
    description: str
    severity : str
    published : bool


class IncidentCreate(BaseModel):
    """Validate the fields accepted when a user reports an incident."""
    incident_type: str
    description: str
    severity : str = "low"
    published : bool = True


class IncidentUpdate(BaseModel):
    """Validate optional fields that may be changed on an incident."""
    incident_type: str | None = None
    description: str | None = None 
    severity : str | None = None
    published : bool | None = None

class IncidentResponse(IncidentBase):
    """Serialize an incident, including its identifiers and reporter."""

    model_config = ConfigDict(from_attributes=True)

    incident_id: int
    reported_at: datetime
    reported_by : int
    reporter : User_response
