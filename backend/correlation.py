"""
BLACKBOX Correlation Engine
Deterministic, explainable event correlation
"""

from sqlalchemy.orm import Session
from models import Event, Incident, IncidentEvent, IncidentStatus
from datetime import datetime, timedelta
from typing import List, Optional


class CorrelationEngine:
    """
    Rule-based correlation engine.
    No ML. No hidden heuristics. Just clear, debuggable logic.
    """

    # Configuration
    ERROR_THRESHOLD = 5  # Number of errors to trigger incident
    TIME_WINDOW_MINUTES = 3  # Rolling window for error detection
    CORRELATION_WINDOW_MINUTES = 10  # Window for correlating related events

    def __init__(self, db: Session):
        self.db = db

    def detect_incidents(self, service: str, environment: str) -> Optional[Incident]:
        """
        Detect if error threshold is crossed for a service.
        Creates incident if threshold exceeded.
        
        Returns:
            Newly created Incident or None
        """
        # Get recent errors in the time window
        window_start = datetime.utcnow() - timedelta(minutes=self.TIME_WINDOW_MINUTES)
        
        error_count = self.db.query(Event).filter(
            Event.service == service,
            Event.environment == environment,
            Event.level == "error",
            Event.timestamp >= window_start
        ).count()

        if error_count >= self.ERROR_THRESHOLD:
            # Check if there's already an open incident for this service
            existing_incident = self.db.query(Incident).filter(
                Incident.primary_service == service,
                Incident.environment == environment,
                Incident.status == IncidentStatus.OPEN
            ).first()

            if not existing_incident:
                # Create new incident
                incident = Incident(
                    primary_service=service,
                    environment=environment,
                    start_time=window_start,
                    status=IncidentStatus.OPEN,
                    severity="high" if error_count >= 10 else "medium"
                )
                self.db.add(incident)
                self.db.commit()
                self.db.refresh(incident)
                return incident

        return None

    def correlate_event_to_incident(self, event: Event) -> None:
        """
        Correlate a single event to relevant incidents.
        Uses three deterministic rules:
        1. Same request_id
        2. Same service within time window
        3. Same environment during incident window
        """
        # Find open incidents that might match this event
        open_incidents = self.db.query(Incident).filter(
            Incident.status == IncidentStatus.OPEN,
            Incident.environment == event.environment
        ).all()

        for incident in open_incidents:
            correlation_reasons = []

            # Rule 1: Same request_id
            if event.request_id:
                existing_correlation = self.db.query(IncidentEvent).join(Event).filter(
                    IncidentEvent.incident_id == incident.id,
                    Event.request_id == event.request_id
                ).first()
                if existing_correlation:
                    correlation_reasons.append("same_request_id")

            # Rule 2: Same service within time window
            if event.service == incident.primary_service:
                time_diff = abs((event.timestamp - incident.start_time).total_seconds() / 60)
                if time_diff <= self.CORRELATION_WINDOW_MINUTES:
                    correlation_reasons.append("same_service_time_window")

            # Rule 3: Same environment during incident window
            if incident.start_time <= event.timestamp:
                if not incident.end_time or event.timestamp <= incident.end_time:
                    correlation_reasons.append("environment_incident_window")

            # If any rule matched, create correlation
            if correlation_reasons:
                # Check if correlation already exists
                existing = self.db.query(IncidentEvent).filter(
                    IncidentEvent.incident_id == incident.id,
                    IncidentEvent.event_id == event.id
                ).first()

                if not existing:
                    incident_event = IncidentEvent(
                        incident_id=incident.id,
                        event_id=event.id,
                        correlation_reason=", ".join(correlation_reasons)
                    )
                    self.db.add(incident_event)

        self.db.commit()

    def get_incident_timeline(self, incident_id: int) -> List[Event]:
        """
        Construct timeline for an incident.
        Returns events in strict chronological order.
        """
        events = self.db.query(Event).join(IncidentEvent).filter(
            IncidentEvent.incident_id == incident_id
        ).order_by(Event.timestamp.asc()).all()

        return events

    def generate_root_cause_summary(self, incident_id: int) -> str:
        """
        Generate probable root cause statement.
        Rule-based, not conclusive.
        """
        events = self.get_incident_timeline(incident_id)
        
        if not events:
            return "No events correlated to this incident."

        incident = self.db.query(Incident).filter(Incident.id == incident_id).first()
        
        # Find first error
        first_error = next((e for e in events if e.level == "error"), None)
        
        # Count error messages
        error_messages = {}
        for event in events:
            if event.level == "error":
                msg = event.message[:100]  # Truncate for grouping
                error_messages[msg] = error_messages.get(msg, 0) + 1

        most_common_error = max(error_messages.items(), key=lambda x: x[1])[0] if error_messages else "unknown"

        # Generate summary
        summary = f"The incident likely originated in the {incident.primary_service} service "
        
        if first_error:
            summary += f"following repeated '{most_common_error}' errors starting at {first_error.timestamp.strftime('%H:%M UTC')}."
        else:
            summary += f"starting at {incident.start_time.strftime('%H:%M UTC')}."

        return summary
