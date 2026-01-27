# BLACKBOX API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication
Version 1.0 does not include authentication. All endpoints are public.

---

## Endpoints

### Health Check

#### `GET /`

Returns service health status.

**Response**
```json
{
  "service": "BLACKBOX",
  "status": "operational",
  "purpose": "incident reasoning platform"
}
```

---

### Events

#### `POST /events`

Ingest a new event into BLACKBOX.

**Request Body**
```json
{
  "service": "payments",
  "environment": "prod",
  "level": "error",
  "message": "Database timeout after 30s",
  "request_id": "req_abc123",
  "timestamp": "2026-01-27T10:42:11Z"
}
```

**Fields**
- `service` (string, required) - Logical service name
- `environment` (string, required) - Environment identifier (prod/staging/dev)
- `level` (string, required) - Event level: `info`, `warning`, or `error`
- `message` (string, required) - Human-readable event description
- `request_id` (string, optional) - Correlation ID for tracking requests
- `timestamp` (string, required) - ISO 8601 timestamp (UTC recommended)

**Response** (201 Created)
```json
{
  "id": 42,
  "service": "payments",
  "environment": "prod",
  "level": "error",
  "message": "Database timeout after 30s",
  "request_id": "req_abc123",
  "timestamp": "2026-01-27T10:42:11Z",
  "received_at": "2026-01-27T10:42:11.234567Z"
}
```

**Notes**
- Events are immutable - no updates or deletes
- If event triggers incident detection, incident is created automatically
- Event is correlated to existing incidents if rules match

---

#### `GET /events`

List recent events.

**Query Parameters**
- `service` (optional) - Filter by service name
- `environment` (optional) - Filter by environment
- `level` (optional) - Filter by level (info/warning/error)
- `limit` (optional, default: 100) - Maximum events to return

**Example**
```
GET /events?service=payments&level=error&limit=50
```

**Response** (200 OK)
```json
[
  {
    "id": 42,
    "service": "payments",
    "environment": "prod",
    "level": "error",
    "message": "Database timeout after 30s",
    "request_id": "req_abc123",
    "timestamp": "2026-01-27T10:42:11Z",
    "received_at": "2026-01-27T10:42:11.234567Z"
  }
]
```

---

### Incidents

#### `GET /incidents`

List all incidents.

**Query Parameters**
- `status` (optional) - Filter by status: `open` or `resolved`
- `environment` (optional) - Filter by environment

**Example**
```
GET /incidents?status=open&environment=prod
```

**Response** (200 OK)
```json
[
  {
    "id": 1,
    "primary_service": "payments",
    "environment": "prod",
    "start_time": "2026-01-27T10:42:00Z",
    "end_time": null,
    "severity": "high",
    "status": "open",
    "created_at": "2026-01-27T10:45:00Z"
  }
]
```

**Notes**
- Incidents are ordered by start_time descending (newest first)
- `end_time` is null for open incidents

---

#### `GET /incidents/{id}`

Get detailed incident information with timeline.

**Path Parameters**
- `id` (integer) - Incident ID

**Response** (200 OK)
```json
{
  "id": 1,
  "primary_service": "payments",
  "environment": "prod",
  "start_time": "2026-01-27T10:42:00Z",
  "end_time": null,
  "severity": "high",
  "status": "open",
  "root_cause_summary": "The incident likely originated in the payments service following repeated 'Database timeout after 30s' errors starting at 10:42 UTC.",
  "timeline": [
    {
      "id": 40,
      "service": "payments",
      "level": "warning",
      "message": "Database connection pool at 80%",
      "request_id": null,
      "timestamp": "2026-01-27T10:41:30Z",
      "correlation_reason": "same_service_time_window"
    },
    {
      "id": 42,
      "service": "payments",
      "level": "error",
      "message": "Database timeout after 30s",
      "request_id": "req_abc123",
      "timestamp": "2026-01-27T10:42:11Z",
      "correlation_reason": "same_service_time_window, environment_incident_window"
    }
  ],
  "event_count": 12
}
```

**Response** (404 Not Found)
```json
{
  "detail": "Incident not found"
}
```

**Notes**
- Timeline events are strictly ordered by timestamp (ascending)
- `correlation_reason` explains why each event was included
- `root_cause_summary` is generated using rule-based logic (not absolute truth)

---

#### `PATCH /incidents/{id}/resolve`

Mark an incident as resolved.

**Path Parameters**
- `id` (integer) - Incident ID

**Response** (200 OK)
```json
{
  "status": "resolved",
  "incident_id": 1
}
```

**Response** (404 Not Found)
```json
{
  "detail": "Incident not found"
}
```

**Notes**
- Sets incident status to `resolved`
- Sets `end_time` to the timestamp of the last correlated event
- Manual resolution only - no automatic resolution

---

## Data Models

### Event

```typescript
interface Event {
  id: number;
  service: string;
  environment: string;
  level: "info" | "warning" | "error";
  message: string;
  request_id: string | null;
  timestamp: string;  // ISO 8601
  received_at: string;  // ISO 8601
}
```

### Incident

```typescript
interface Incident {
  id: number;
  primary_service: string;
  environment: string;
  start_time: string;  // ISO 8601
  end_time: string | null;  // ISO 8601
  severity: string | null;
  status: "open" | "resolved";
  created_at: string;  // ISO 8601
}
```

### Timeline Event

```typescript
interface TimelineEvent {
  id: number;
  service: string;
  level: "info" | "warning" | "error";
  message: string;
  request_id: string | null;
  timestamp: string;  // ISO 8601
  correlation_reason: string;  // e.g., "same_request_id, same_service_time_window"
}
```

---

## Correlation Rules

Events are automatically correlated to incidents using three deterministic rules:

### 1. Same Request ID
Events with matching `request_id` values are correlated.

**Example**:
- Event A: `request_id = "req_123"`
- Event B: `request_id = "req_123"`
- Result: Correlated (reason: `same_request_id`)

### 2. Same Service within Time Window
Events from the same service within 10 minutes of incident start.

**Example**:
- Incident started: 10:00 UTC in `payments` service
- Event: `payments` service at 10:05 UTC
- Result: Correlated (reason: `same_service_time_window`)

### 3. Same Environment during Incident Window
Events in the same environment during an active incident.

**Example**:
- Incident: `environment = "prod"`, active 10:00-10:30
- Event: `environment = "prod"` at 10:15 UTC
- Result: Correlated (reason: `environment_incident_window`)

**Multiple Rules**
If multiple rules match, all are listed in `correlation_reason`:
```
"same_request_id, same_service_time_window, environment_incident_window"
```

---

## Incident Detection

Incidents are **automatically created** when:
- **5 or more** error-level events
- From the **same service**
- Within a **3-minute** rolling window

**Configuration** (in `correlation.py`):
```python
ERROR_THRESHOLD = 5
TIME_WINDOW_MINUTES = 3
```

**Example Timeline**:
```
10:00 - Error 1 in payments
10:01 - Error 2 in payments
10:02 - Error 3 in payments
10:02 - Error 4 in payments
10:03 - Error 5 in payments  ← Incident created here
```

---

## Error Responses

### 400 Bad Request
Invalid request data.

```json
{
  "detail": [
    {
      "loc": ["body", "level"],
      "msg": "value is not a valid enumeration member; permitted: 'info', 'warning', 'error'",
      "type": "type_error.enum"
    }
  ]
}
```

### 404 Not Found
Resource not found.

```json
{
  "detail": "Incident not found"
}
```

### 422 Unprocessable Entity
Request validation failed.

```json
{
  "detail": [
    {
      "loc": ["body", "timestamp"],
      "msg": "invalid datetime format",
      "type": "value_error.datetime"
    }
  ]
}
```

---

## Rate Limiting

Version 1.0 does not include rate limiting. Consider implementing in production:
- Use reverse proxy (nginx) for rate limiting
- Or add middleware in FastAPI

---

## Example Workflows

### Workflow 1: Send Events from Application

```python
import requests
from datetime import datetime

def send_event(service, level, message, request_id=None):
    event = {
        "service": service,
        "environment": "prod",
        "level": level,
        "message": message,
        "request_id": request_id,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    response = requests.post(
        "http://localhost:8000/events",
        json=event
    )
    return response.json()

# Usage
send_event("payments", "error", "Database timeout", "req_123")
```

### Workflow 2: Query Recent Incidents

```python
import requests

# Get all open incidents
response = requests.get(
    "http://localhost:8000/incidents",
    params={"status": "open"}
)
incidents = response.json()

# Get details for first incident
if incidents:
    incident_id = incidents[0]["id"]
    detail = requests.get(
        f"http://localhost:8000/incidents/{incident_id}"
    ).json()
    
    print(f"Root Cause: {detail['root_cause_summary']}")
    print(f"Events: {detail['event_count']}")
```

### Workflow 3: Integrate with Logging Library

```python
import logging
import requests
from datetime import datetime

class BlackboxHandler(logging.Handler):
    def __init__(self, service_name, environment="prod"):
        super().__init__()
        self.service = service_name
        self.environment = environment
        self.api_url = "http://localhost:8000/events"
    
    def emit(self, record):
        level_map = {
            logging.INFO: "info",
            logging.WARNING: "warning",
            logging.ERROR: "error",
        }
        
        event = {
            "service": self.service,
            "environment": self.environment,
            "level": level_map.get(record.levelno, "info"),
            "message": record.getMessage(),
            "request_id": getattr(record, 'request_id', None),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        try:
            requests.post(self.api_url, json=event)
        except:
            pass  # Don't let logging errors break the application

# Usage
logger = logging.getLogger("payments")
logger.addHandler(BlackboxHandler("payments", "prod"))
logger.error("Database timeout")
```

---

## Interactive Documentation

FastAPI provides automatic interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These interfaces allow you to:
- View all endpoints
- See request/response schemas
- Test API calls directly
- Download OpenAPI specification

---

## OpenAPI Specification

Download the OpenAPI (Swagger) specification:

```bash
curl http://localhost:8000/openapi.json > blackbox-api-spec.json
```

Use this specification for:
- Generating client libraries
- API testing tools
- Documentation generation
- Contract validation

---

For deployment information, see [DEPLOYMENT.md](DEPLOYMENT.md)
