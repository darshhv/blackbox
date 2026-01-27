# BLACKBOX - Incident Reasoning Platform

> A web-based incident reasoning platform that reconstructs failure timelines by correlating events across services, helping engineers understand what happened before deciding why.

## What BLACKBOX Is

BLACKBOX is a **flight data recorder for software systems**. It helps engineers understand failures, not just detect them.

### Core Purpose
- Reconstruct what happened during system failures
- Display events in correct chronological order
- Correlate events across services
- Reduce cognitive load during incidents

### What BLACKBOX Is NOT
- ❌ A prediction system
- ❌ An auto-fix tool
- ❌ An alerting/paging system
- ❌ A replacement for engineers

## Design Philosophy

1. **Sequence over severity** - Order matters more than error level
2. **Correlation before explanation** - Events must be grouped before interpretation
3. **Structure over intelligence** - Clear structure beats AI guessing
4. **Human reasoning stays in control** - Assists thinking, doesn't replace it
5. **Calm systems produce calm engineers** - Reduced noise leads to better decisions

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Web Dashboard                        │
│              (React - Calm, Minimal UI)                 │
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│                   FastAPI Backend                       │
│  ┌──────────────────────────────────────────────────┐  │
│  │          Event Ingestion Layer                   │  │
│  │  POST /events - Immutable event storage          │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │       Correlation & Incident Engine              │  │
│  │  • Deterministic rule-based correlation          │  │
│  │  • No ML, fully explainable                      │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │         Incident Timeline Builder                │  │
│  │  Chronological sequence reconstruction           │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│                   PostgreSQL                            │
│  • events - Immutable event log                        │
│  • incidents - Detected failure windows                │
│  • incident_events - Correlation mappings              │
└─────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Or: Python 3.11+, Node 18+, PostgreSQL 15+

### Using Docker (Recommended)

```bash
# Clone or navigate to the project
cd blackbox

# Start all services
docker-compose up

# The application will be available at:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

### Manual Setup

#### 1. Database Setup
```bash
# Start PostgreSQL
createdb blackbox
createuser blackbox --password  # password: blackbox
```

#### 2. Backend Setup
```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Set database URL (optional, defaults to localhost)
export DATABASE_URL=postgresql://blackbox:blackbox@localhost:5432/blackbox

# Run backend
python main.py

# Backend runs on http://localhost:8000
```

#### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Frontend runs on http://localhost:3000
```

## Usage

### Sending Events

Events are sent via REST API:

```bash
POST http://localhost:8000/events
Content-Type: application/json

{
  "service": "payments",
  "environment": "prod",
  "level": "error",
  "message": "Database timeout after 30s",
  "request_id": "req_abc123",
  "timestamp": "2026-01-27T10:42:11Z"
}
```

#### Event Schema
- `service` - Service name emitting the event
- `environment` - prod/staging/dev
- `level` - info/warning/error
- `message` - Human-readable description
- `request_id` - Optional, critical for correlation
- `timestamp` - Source-of-truth time (ISO 8601)

### Incident Detection

Incidents are **automatically created** when:
- 5+ error events
- From the same service
- Within a 3-minute window

### Correlation Rules

Events are correlated to incidents using three deterministic rules:

1. **Same request_id** - Events with matching request IDs
2. **Same service within time window** - Events from the same service within 10 minutes
3. **Same environment during incident** - Events in the same environment during an active incident

All correlation is **explainable and auditable**.

### Viewing Incidents

1. Navigate to http://localhost:3000
2. View list of all incidents
3. Click an incident to see:
   - Root cause summary (probable, not absolute)
   - Complete timeline in chronological order
   - Correlation reasons for each event

## API Endpoints

### Events
- `POST /events` - Ingest new event
- `GET /events` - List events (with filters)

### Incidents
- `GET /incidents` - List all incidents
- `GET /incidents/{id}` - Get incident details with timeline
- `PATCH /incidents/{id}/resolve` - Mark incident as resolved

### Documentation
- Interactive API docs: http://localhost:8000/docs

## Example Workflow

### Simulating an Incident

```bash
# Generate error events to trigger incident detection
for i in {1..6}; do
  curl -X POST http://localhost:8000/events \
    -H "Content-Type: application/json" \
    -d "{
      \"service\": \"payments\",
      \"environment\": \"prod\",
      \"level\": \"error\",
      \"message\": \"Database connection timeout\",
      \"request_id\": \"req_$i\",
      \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"
    }"
  sleep 2
done
```

This will:
1. Create 6 error events
2. Trigger incident detection (threshold: 5 errors)
3. Auto-correlate all events to the incident
4. Generate a root cause summary

Visit http://localhost:3000 to see the incident and timeline.

## Project Structure

```
blackbox/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── models.py            # Database models
│   ├── database.py          # Database config
│   ├── correlation.py       # Correlation engine
│   ├── schemas.py           # Pydantic schemas
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── IncidentsList.jsx
│   │   │   └── IncidentDetail.jsx
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   ├── vite.config.js
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## Configuration

### Backend Configuration
- `DATABASE_URL` - PostgreSQL connection string
- Default: `postgresql://blackbox:blackbox@localhost:5432/blackbox`

### Correlation Configuration (in `correlation.py`)
- `ERROR_THRESHOLD = 5` - Errors needed to trigger incident
- `TIME_WINDOW_MINUTES = 3` - Rolling window for detection
- `CORRELATION_WINDOW_MINUTES = 10` - Window for event correlation

## Design Decisions

### Why No Kubernetes?
- Complexity adds no value for this use case
- Local deployability is essential
- Focus is on reasoning, not YAML

### Why Rule-Based Correlation?
- **Trust** - Engineers must trust grouping logic
- **Debuggability** - You can debug the debugger
- **Explainability** - Every correlation has a clear reason
- **Predictability** - Same inputs always produce same outputs

### Why Immutable Events?
- Trust in the data layer
- No possibility of retroactive manipulation
- Clear audit trail

### Why No AI/ML?
- Explainability over cleverness
- Deterministic behavior
- No hidden heuristics
- You can prove it works correctly

## What BLACKBOX Demonstrates

Building BLACKBOX proves:
- ✅ Systems thinking
- ✅ Data modeling skills
- ✅ Debugging mindset
- ✅ Trade-off awareness
- ✅ Product restraint
- ✅ Engineering taste

## Contributing

This is a reference implementation. The value is in understanding the design decisions, not in feature additions.

## Philosophy

> "BLACKBOX is not a tool for speed. BLACKBOX is a tool for clarity under pressure. Its core value is not automation. Its core value is slowing failures down enough to think clearly."

## License

MIT License - See LICENSE file for details

## Interview Usage

One-sentence explanation:
> "BLACKBOX is a web-based incident reasoning system that reconstructs failure timelines by correlating events across services, helping engineers understand what happened before deciding why."

Key talking points:
- Focuses on post-event clarity, not prediction
- Deterministic correlation over ML
- Timeline is the hero of the UI
- Calm, minimal interface reduces cognitive load
- Immutable event storage builds trust
