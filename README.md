# BLACKBOX

> A web-based incident reasoning platform for understanding system failures through event correlation and timeline reconstruction.

**Live Demo:** [https://blackbox-frontend-hwy0.onrender.com](https://blackbox-frontend-hwy0.onrender.com)

---

## Overview

BLACKBOX is a production-ready incident analysis platform designed to help engineers understand system failures by reconstructing timelines from distributed events. Rather than focusing on detection or alerting, BLACKBOX provides post-event clarity by correlating events across services and presenting them in chronological sequence.

The platform operates on a core principle: **sequence before interpretation**. By forcing engineers to understand the order of events before jumping to conclusions, BLACKBOX reduces cognitive load during incident response and enables more accurate root cause analysis.

### Key Characteristics

- **Deterministic correlation** — Three explicit rules, no machine learning
- **Immutable event storage** — Write-only data model for auditability
- **Timeline-focused interface** — Chronological ordering as the primary view
- **Explainable reasoning** — Every correlation decision is documented
- **Calm design** — Minimal UI to reduce stress during incidents

---

## Architecture

BLACKBOX consists of three primary components:

```
Frontend (React)
    ↓
Backend API (FastAPI)
    ↓
Database (PostgreSQL)
```

### Technology Stack

**Backend**
- FastAPI (Python 3.11)
- SQLAlchemy ORM
- PostgreSQL 15
- Pydantic validation

**Frontend**
- React 18
- Vite build system
- Axios for API communication
- React Router for navigation

**Infrastructure**
- Render (deployment platform)
- Docker (containerization)
- GitHub Actions (CI/CD ready)

---

## Core Concepts

### Event Model

Events are immutable records representing something that occurred in a system:

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

All events are stored permanently without modification or deletion.

### Incident Detection

Incidents are automatically created when error thresholds are exceeded:

- **Threshold:** 5 error-level events
- **Time Window:** 3 minutes (rolling)
- **Scope:** Per service, per environment

This threshold-based approach is simple, predictable, and configurable.

### Correlation Rules

Events are correlated to incidents using three deterministic rules:

1. **Same Request ID** — Events sharing a request identifier
2. **Same Service within Time Window** — Events from the same service within 10 minutes
3. **Same Environment during Incident** — Events in the environment during an active incident

Each correlation includes the specific rule(s) that matched, making the decision process transparent and debuggable.

### Timeline Reconstruction

The timeline view presents all correlated events in strict chronological order, grouped by service. This preserves the actual sequence of events and enables pattern recognition across distributed systems.

---

## Installation

### Prerequisites

- Python 3.11 or higher
- Node.js 18 or higher
- PostgreSQL 15 or higher

### Local Development

**1. Clone the repository**

```bash
git clone https://github.com/darshhv/blackbox.git
cd blackbox
```

**2. Set up the database**

```bash
createdb blackbox
createuser blackbox --password
# Enter password: blackbox
```

```sql
GRANT ALL PRIVILEGES ON DATABASE blackbox TO blackbox;
```

**3. Configure environment**

```bash
export DATABASE_URL=postgresql://blackbox:blackbox@localhost:5432/blackbox
```

**4. Start the backend**

```bash
cd backend
pip install -r requirements.txt
python main.py
```

Backend runs on `http://localhost:8000`

**5. Start the frontend**

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:3000`

---

## Deployment

### Render Deployment

BLACKBOX is designed for straightforward deployment on Render.

**Database**

1. Create PostgreSQL database
2. Copy the Internal Database URL

**Backend Service**

1. Connect GitHub repository
2. Configure service:
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
3. Add environment variable:
   - `DATABASE_URL`: [Internal Database URL from step 1]

**Frontend Service**

1. Connect the same GitHub repository
2. Configure service:
   - **Root Directory:** `frontend`
   - **Build Command:** `npm install && npm run build`
   - **Publish Directory:** `dist`
3. Update `frontend/src/services/api.js` with backend URL

### Alternative Platforms

The application can be deployed to any platform supporting:
- Python WSGI applications
- Node.js static site hosting
- PostgreSQL databases

Tested on: Render, Railway, Heroku, Vercel (frontend), AWS

---

## Usage

### API Documentation

Interactive API documentation is available at `/docs` when the backend is running.

**Example: Creating an Event**

```bash
curl -X POST https://your-backend-url.com/events \
  -H "Content-Type: application/json" \
  -d '{
    "service": "payments",
    "environment": "prod",
    "level": "error",
    "message": "Database connection timeout",
    "request_id": "req_001",
    "timestamp": "2026-01-27T10:00:00Z"
  }'
```

**Example: Listing Incidents**

```bash
curl https://your-backend-url.com/incidents
```

**Example: Incident Details**

```bash
curl https://your-backend-url.com/incidents/1
```

### Creating an Incident

To trigger incident detection, send 5 or more error events from the same service within a 3-minute window:

```bash
for i in {1..6}; do
  curl -X POST https://your-backend-url.com/events \
    -H "Content-Type: application/json" \
    -d "{
      \"service\": \"api-gateway\",
      \"environment\": \"prod\",
      \"level\": \"error\",
      \"message\": \"Service unavailable\",
      \"request_id\": \"req_$i\",
      \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"
    }"
  sleep 1
done
```

The incident will appear immediately in the web interface.

---

## Design Philosophy

### Sequence Over Severity

Order matters more than error levels. A warning that occurs before an error may be more important than the error itself. BLACKBOX preserves temporal sequence as the primary organizing principle.

### Correlation Before Explanation

Events must be grouped accurately before attempting to explain what happened. The correlation engine uses simple, deterministic rules rather than heuristics or machine learning to ensure grouping decisions are predictable and debuggable.

### Structure Over Intelligence

Clear data structures and explicit logic are more valuable than sophisticated algorithms. Every decision in BLACKBOX is traceable and explainable.

### Human Reasoning Stays in Control

The platform assists engineers in understanding failures but does not attempt to replace human judgment. Root cause summaries are framed as "likely" rather than definitive.

### Calm Systems Produce Calm Engineers

The interface is deliberately minimal to reduce visual noise during high-stress incidents. No charts, no animations, no distractions—just the timeline and the facts.

---

## Configuration

### Backend Configuration

Located in `backend/correlation.py`:

```python
ERROR_THRESHOLD = 5              # Errors to trigger incident
TIME_WINDOW_MINUTES = 3          # Rolling detection window
CORRELATION_WINDOW_MINUTES = 10  # Event correlation window
```

### Database Schema

The database uses three primary tables:

**events** — Immutable event log
- Indexed by timestamp, service, request_id
- No updates or deletes permitted

**incidents** — Detected failure windows
- Tracks service, environment, status
- Start and end times

**incident_events** — Correlation mappings
- Links events to incidents
- Stores correlation reasoning

---

## API Reference

### POST /events

Ingest a new event.

**Request Body**
```json
{
  "service": "string",
  "environment": "string",
  "level": "info|warning|error",
  "message": "string",
  "request_id": "string (optional)",
  "timestamp": "ISO 8601 datetime"
}
```

**Response:** 201 Created

### GET /incidents

List all incidents.

**Query Parameters**
- `status` — Filter by open/resolved
- `environment` — Filter by environment

**Response:** Array of incident summaries

### GET /incidents/{id}

Get incident details with full timeline.

**Response:** Incident object with correlated events

### PATCH /incidents/{id}/resolve

Mark incident as resolved.

**Response:** Updated incident status

---

## Project Structure

```
blackbox/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── models.py            # Database models
│   ├── schemas.py           # Pydantic schemas
│   ├── correlation.py       # Correlation engine
│   ├── database.py          # Database configuration
│   └── requirements.txt     # Python dependencies
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
│   └── vite.config.js
├── database/
│   └── generate_sample_data.py
└── README.md
```

---

## Design Decisions

### Why Rule-Based Correlation?

Machine learning would introduce unpredictability in a system where trust is critical. Engineers must be able to verify correlation decisions. Rule-based logic is:
- Completely deterministic
- Fully debuggable
- Easily auditable
- Understandable by all team members

### Why Immutable Events?

Allowing event modification would undermine trust in the timeline. Immutability provides:
- Clear audit trail
- No possibility of retroactive changes
- Single source of truth
- Simplified debugging

### Why No Alerting?

BLACKBOX operates after alerts have already fired. It exists to help engineers understand what happened, not to notify them that something is happening. This focused scope prevents feature creep and maintains clarity of purpose.

### Why Timeline as Primary View?

Most incident tools focus on aggregation and statistics. BLACKBOX prioritizes sequence because:
- Causal relationships emerge from ordering
- Engineers think in terms of "what happened first"
- Timelines reveal cascade failures
- Chronological views are universally understood

---

## Limitations

### Deliberate Exclusions

The following features are intentionally not included in version 1.0:

- Authentication and authorization
- Multi-tenant organizations
- Alert/paging integration
- Real-time event streaming
- Metric visualization
- Distributed tracing integration
- Machine learning or AI
- Event search and filtering (UI)
- Automatic incident resolution

These exclusions reflect design restraint and focus on core functionality.

### Known Constraints

- **Timestamp-based detection:** Incident detection uses event timestamps, not ingestion time
- **Single-environment isolation:** Events from different environments never correlate
- **No event updates:** Once created, events cannot be modified
- **Manual resolution:** Incidents must be manually marked as resolved

---

## Contributing

Contributions are welcome. Please follow these guidelines:

1. **Maintain the philosophy** — Any contribution should align with the core design principles
2. **Preserve explainability** — New features must be deterministic and debuggable
3. **Document reasoning** — Explain the "why" behind technical decisions
4. **Test thoroughly** — Include tests for new functionality
5. **Keep it simple** — Favor clarity over cleverness

### Development Process

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Update documentation
6. Submit a pull request

---

## Testing

### Manual Testing

Use the sample data generator:

```bash
cd database
python generate_sample_data.py
```

Choose from predefined scenarios:
1. Database timeout incident
2. Deployment failure
3. Cascading service failure
4. Multi-environment events

### API Testing

Interactive testing via Swagger UI:
```
http://localhost:8000/docs
```

---

## Performance Considerations

### Database Indexing

The schema includes indexes on:
- `events.timestamp`
- `events.service`
- `events.request_id`
- `events.environment`

These support efficient incident detection and correlation queries.

### Scaling Guidance

For high-volume deployments:
- Partition events table by timestamp
- Add read replicas for query load
- Implement event batching for ingestion
- Consider time-series database for events

The current implementation is optimized for clarity and maintainability, not maximum throughput.

---

## License

MIT License

Copyright (c) 2026 BLACKBOX Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

---

## Acknowledgments

Built to demonstrate systems thinking, data modeling, and production deployment capabilities. Designed with the principle that calm systems produce calm engineers.

**Author:** Darshan Reddy V  
**Repository:** [github.com/darshhv/blackbox](https://github.com/darshhv/blackbox)  
**Live Demo:** [blackbox-frontend-hwy0.onrender.com](https://blackbox-frontend-hwy0.onrender.com)  

---

## Support

For questions, issues, or discussions:
- **Issues:** GitHub Issues
- **Documentation:** See `/docs` folder
- **API Reference:** `/docs` endpoint when running

---

**BLACKBOX** — Understanding failures through sequence.
