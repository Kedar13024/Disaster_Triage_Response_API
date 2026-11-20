"""Pydantic request and response schemas for incident endpoints."""


from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

from backend.schemas.user_sch import User_response

class IncidentType(StrEnum):
    FLOOD = "Flood"
    EARTHQUAKE = "Earthquake"
    FIRE = "Fire"
    LANDSLIDE = "Landslide"
    CYCLONE = "Cyclone"
    MED_EM = "Medical Emergency"
    OTHER = "Other"

class IncidentBase(BaseModel):
    """An incident returned by the API."""

    incident_type: IncidentType
    description: str
    severity : str
    published : bool


class IncidentCreate(BaseModel):
    """Validate the fields accepted when a user reports an incident."""

    model_config = ConfigDict(
        extra="forbid", str_strip_whitespace=True
        )

    incident_type: IncidentType
    description: str = Field(min_length=10 , max_length=2000)


class IncidentUpdate(BaseModel):
    """Validate optional fields that may be changed on an incident."""

    model_config = ConfigDict(
        extra="forbid" ,  str_strip_whitespace=True
        )

    incident_type: IncidentType | None = None
    description: str | None = Field(min_length=10 , max_length=2000 , default=None)

class IncidentResponse(IncidentBase):
    """Serialize an incident, including its identifiers and reporter."""

    model_config = ConfigDict(from_attributes=True)

    incident_id: int
    reported_at: datetime
    reported_by : int
    reporter : User_response
