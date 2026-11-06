from pydantic import BaseModel, ConfigDict
from datetime import datetime

class IncidentBase(BaseModel):
    """An incident returned by the API."""

    incident_type: str
    description: str
    severity : str
    published : bool


class IncidentCreate(BaseModel):
    """Fields needed to report  an incident."""
    incident_type: str
    description: str
    severity : str = "low"
    published : bool = True


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
