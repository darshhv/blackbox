"""
BLACKBOX Database Models
Immutable event storage and incident correlation
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


class EventLevel(str, enum.Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class IncidentStatus(str, enum.Enum):
    OPEN = "open"
    RESOLVED = "resolved"


class Event(Base):
    """
    Immutable event storage.
    Events are write-only - no updates or deletes.
    """
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    service = Column(String(255), nullable=False, index=True)
    environment = Column(String(50), nullable=False, index=True)
    level = Column(Enum(EventLevel), nullable=False)
    message = Column(Text, nullable=False)
    request_id = Column(String(255), nullable=True, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    received_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    incident_associations = relationship("IncidentEvent", back_populates="event")

    def __repr__(self):
        return f"<Event(id={self.id}, service={self.service}, level={self.level}, timestamp={self.timestamp})>"


class Incident(Base):
    """
    Represents a detected failure window.
    Created when error threshold is crossed.
    """
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    primary_service = Column(String(255), nullable=False, index=True)
    environment = Column(String(50), nullable=False, index=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    severity = Column(String(50), nullable=True)
    status = Column(Enum(IncidentStatus), nullable=False, default=IncidentStatus.OPEN)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    event_associations = relationship("IncidentEvent", back_populates="incident")

    def __repr__(self):
        return f"<Incident(id={self.id}, service={self.primary_service}, status={self.status})>"


class IncidentEvent(Base):
    """
    Join table mapping events to incidents.
    Makes correlation explainable and auditable.
    """
    __tablename__ = "incident_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False, index=True)
    correlation_reason = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    incident = relationship("Incident", back_populates="event_associations")
    event = relationship("Event", back_populates="incident_associations")

    def __repr__(self):
        return f"<IncidentEvent(incident_id={self.incident_id}, event_id={self.event_id}, reason={self.correlation_reason})>"
