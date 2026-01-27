"""
BLACKBOX API Schemas
Pydantic models for request/response validation
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class EventLevel(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class IncidentStatus(str, Enum):
    OPEN = "open"
    RESOLVED = "resolved"


class EventCreate(BaseModel):
    """
    Schema for event ingestion.
    Fixed, intentional structure.
    """
    service: str = Field(..., description="Logical service name")
    environment: str = Field(..., description="Environment (prod/staging/dev)")
    level: EventLevel = Field(..., description="Event level")
    message: str = Field(..., description="Human-readable description")
    request_id: Optional[str] = Field(None, description="Optional correlation ID")
    timestamp: datetime = Field(..., description="Source-of-truth time")

    class Config:
        json_schema_extra = {
            "example": {
                "service": "payments",
                "environment": "prod",
                "level": "error",
                "message": "Database timeout",
                "request_id": "abc123",
                "timestamp": "2026-02-03T10:42:11Z"
            }
        }


class EventResponse(BaseModel):
    """Response after event ingestion"""
    id: int
    service: str
    environment: str
    level: str
    message: str
    request_id: Optional[str]
    timestamp: datetime
    received_at: datetime

    class Config:
        from_attributes = True


class IncidentSummary(BaseModel):
    """Incident list view"""
    id: int
    primary_service: str
    environment: str
    start_time: datetime
    end_time: Optional[datetime]
    severity: Optional[str]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class TimelineEvent(BaseModel):
    """Event in timeline view"""
    id: int
    service: str
    level: str
    message: str
    request_id: Optional[str]
    timestamp: datetime
    correlation_reason: str

    class Config:
        from_attributes = True


class IncidentDetail(BaseModel):
    """Complete incident detail with timeline"""
    id: int
    primary_service: str
    environment: str
    start_time: datetime
    end_time: Optional[datetime]
    severity: Optional[str]
    status: str
    root_cause_summary: str
    timeline: List[TimelineEvent]
    event_count: int

    class Config:
        from_attributes = True
