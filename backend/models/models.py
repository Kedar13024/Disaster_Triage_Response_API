"""SQLAlchemy ORM models for incidents """

from backend.database.database import Base

from sqlalchemy import (
    TIMESTAMP,
    Boolean,
    Column,
    Integer,
    String,
    text,
)

class Incident(Base):
    """Represent an incident reported by a user.

    Attributes:
        incident_id: Primary key of the incident.
        incident_type: Category of the incident.
        description: Details supplied by the reporter.
        severity: Urgency level of the incident.
        published: Whether the incident is publicly visible.
        reported_at: Timestamp when the incident was created.
    """

    __tablename__ = "incidents"
    incident_id = Column(Integer , primary_key=True , nullable=False)
    incident_type = Column(String, nullable=False)
    description = Column(String , nullable=False)
    severity = Column(String , nullable=False , server_default="low")
    published = Column(Boolean , nullable=False , server_default='TRUE')
    reported_at = Column(TIMESTAMP(timezone=True), nullable=False , server_default=text('now()'))