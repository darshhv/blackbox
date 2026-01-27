"""
BLACKBOX API
Web-based incident reasoning platform
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from database import get_db, init_db
from models import Event, Incident, IncidentEvent, IncidentStatus
from schemas import (
    EventCreate, EventResponse, IncidentSummary, 
    IncidentDetail, TimelineEvent
)
from correlation import CorrelationEngine

app = FastAPI(
    title="BLACKBOX",
    description="Incident reasoning platform for understanding failures",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    """Initialize database on startup"""
    init_db()


@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "service": "BLACKBOX",
        "status": "operational",
        "purpose": "incident reasoning platform"
    }


@app.post("/events", response_model=EventResponse, status_code=201)
def create_event(event: EventCreate, db: Session = Depends(get_db)):
    """
    Event ingestion endpoint.
    
    Events are immutable - write-only storage.
    No updates or deletes allowed.
    """
    # Create event (immutable)
    db_event = Event(
        service=event.service,
        environment=event.environment,
        level=event.level,
        message=event.message,
        request_id=event.request_id,
        timestamp=event.timestamp
    )
    
    db.add(db_event)
    db.commit()
    db.refresh(db_event)

    # Run correlation logic
    correlation_engine = CorrelationEngine(db)
    
    # Check if this triggers incident detection
    if db_event.level == "error":
        incident = correlation_engine.detect_incidents(
            service=db_event.service,
            environment=db_event.environment
        )
        if incident:
            print(f"New incident detected: {incident.id}")
    
    # Correlate event to existing incidents
    correlation_engine.correlate_event_to_incident(db_event)

    return db_event


@app.get("/incidents", response_model=List[IncidentSummary])
def list_incidents(
    status: str = None,
    environment: str = None,
    db: Session = Depends(get_db)
):
    """
    List all incidents.
    Optional filters: status, environment
    """
    query = db.query(Incident)
    
    if status:
        query = query.filter(Incident.status == status)
    if environment:
        query = query.filter(Incident.environment == environment)
    
    incidents = query.order_by(Incident.start_time.desc()).all()
    return incidents


@app.get("/incidents/{incident_id}", response_model=IncidentDetail)
def get_incident(incident_id: int, db: Session = Depends(get_db)):
    """
    Get detailed incident view with timeline.
    This is the primary analysis interface.
    """
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    # Generate correlation engine
    correlation_engine = CorrelationEngine(db)
    
    # Get timeline
    events = correlation_engine.get_incident_timeline(incident_id)
    
    # Build timeline with correlation reasons
    timeline = []
    for event in events:
        correlation = db.query(IncidentEvent).filter(
            IncidentEvent.incident_id == incident_id,
            IncidentEvent.event_id == event.id
        ).first()
        
        timeline.append(TimelineEvent(
            id=event.id,
            service=event.service,
            level=event.level,
            message=event.message,
            request_id=event.request_id,
            timestamp=event.timestamp,
            correlation_reason=correlation.correlation_reason if correlation else "unknown"
        ))
    
    # Generate root cause summary
    root_cause = correlation_engine.generate_root_cause_summary(incident_id)

    return IncidentDetail(
        id=incident.id,
        primary_service=incident.primary_service,
        environment=incident.environment,
        start_time=incident.start_time,
        end_time=incident.end_time,
        severity=incident.severity,
        status=incident.status,
        root_cause_summary=root_cause,
        timeline=timeline,
        event_count=len(timeline)
    )


@app.patch("/incidents/{incident_id}/resolve")
def resolve_incident(incident_id: int, db: Session = Depends(get_db)):
    """
    Mark incident as resolved.
    Manual resolution only - no auto-resolution.
    """
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    incident.status = IncidentStatus.RESOLVED
    incident.end_time = incident.end_time or db.query(Event).join(IncidentEvent).filter(
        IncidentEvent.incident_id == incident_id
    ).order_by(Event.timestamp.desc()).first().timestamp
    
    db.commit()
    
    return {"status": "resolved", "incident_id": incident_id}


@app.get("/events", response_model=List[EventResponse])
def list_events(
    service: str = None,
    environment: str = None,
    level: str = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List raw events.
    Primarily for debugging.
    """
    query = db.query(Event)
    
    if service:
        query = query.filter(Event.service == service)
    if environment:
        query = query.filter(Event.environment == environment)
    if level:
        query = query.filter(Event.level == level)
    
    events = query.order_by(Event.timestamp.desc()).limit(limit).all()
    return events


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
