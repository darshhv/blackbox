# BLACKBOX

A web-based incident reasoning platform for reconstructing failure timelines through event correlation across distributed services.

## Overview

BLACKBOX helps engineers understand system failures by presenting events in chronological order and correlating them across services. Unlike traditional monitoring tools that focus on alerting, BLACKBOX focuses on post-incident clarity and understanding.

**Core Philosophy:** Sequence before interpretation. Force clarity under pressure.

## Live Demo

- **Application:** https://blackbox-frontend-hwy0.onrender.com
- **API Documentation:** https://blackbox-33n9.onrender.com/docs
- **Source Code:** https://github.com/darshhv/blackbox

## Features

- **Automatic Incident Detection** - Configurable threshold-based detection (default: 5 errors within 3 minutes)
- **Rule-Based Correlation** - Three deterministic rules for explainable event grouping
- **Timeline Reconstruction** - Chronological event ordering across services
- **Root Cause Analysis** - Automated probable cause summary generation
- **Immutable Event Storage** - Write-only event log for data integrity
- **Clean Interface** - Minimal design focused on reducing cognitive load

## Design Principles

1. **Sequence over severity** - Order matters more than error level
2. **Correlation before explanation** - Group events before interpreting them
3. **Structure over intelligence** - Clear rules beat heuristics
4. **Human reasoning stays in control** - Assist thinking, don't replace it
5. **Calm systems produce calm engineers** - Reduce noise to improve decisions

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Web Dashboard                        │
│                  (React Frontend)                       │
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│                   FastAPI Backend                       │
│  ┌──────────────────────────────────────────────────┐   │
│  │          Event Ingestion Layer                   │   │
│  │  POST /events - Immutable event storage          │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │       Correlation & Incident Engine              │   │
│  │  Deterministic rule-based correlation            │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │         Incident Timeline Builder                │   │
│  │  Chronological sequence reconstruction           │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│                   PostgreSQL                            │
│  - events (immutable event log)                         │
│  - incidents (detected failure windows)                 │
│  - incident_events (correlation mappings)               │
└─────────────────────────────────────────────────────────┘
```

## Technology Stack

**Backend**
- FastAPI (Python 3.11)
- PostgreSQL 15
- SQLAlchemy ORM
- Pydantic for validation

**Frontend**
- React 18
- Vite build tool
- Axios for API communication
- React Router for navigation

**Deployment**
- Docker containerization
- Render.com hosting
- GitHub Actions for CI/CD

## Installation

### Prerequisites

- Python 3.11 or higher
- Node.js 18 or higher
- PostgreSQL 15 or higher
- Docker (optional)

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
# Password: blackbox (or your choice)
```

**3. Configure environment variables**

```bash
# Backend
export DATABASE_URL=postgresql://blackbox:blackbox@localhost:5432/blackbox

# Frontend (optional)
export VITE_API_URL=http://localhost:8000
```

**4. Start the backend**

```bash
cd backend
pip install -r requirements.txt
python main.py
```

Backend runs on http://localhost:8000

**5. Start the frontend**

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on http://localhost:3000

### Docker Deployment

```bash
docker-compose up
```

Services will be available at:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Database: localhost:5432

## Usage

### Creating Events

Events are sent via the REST API with a fixed schema:

```bash
curl -X POST http://localhost:8000/events \
  -H "Content-Type: application/json" \
  -d '{
    "service": "payments",
    "environment": "prod",
    "level": "error",
    "message": "Database connection timeout after 30s",
    "request_id": "req_abc123",
    "timestamp": "2026-01-27T10:42:11Z"
  }'
```

**Event Schema**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| service | string | Yes | Service name emitting the event |
| environment | string | Yes | Environment identifier (prod/staging/dev) |
| level | enum | Yes | Event level: info, warning, or error |
| message | string | Yes | Human-readable event description |
| request_id | string | No | Optional correlation ID for distributed tracing |
| timestamp | datetime | Yes | ISO 8601 timestamp (UTC recommended) |

### Incident Detection

Incidents are automatically created when error thresholds are exceeded:

- **Threshold:** 5 error events
- **Time Window:** 3 minutes
- **Scope:** Per service, per environment

Configuration can be modified in `backend/correlation.py`:

```python
ERROR_THRESHOLD = 5
TIME_WINDOW_MINUTES = 3
```

### Correlation Rules

Events are correlated to incidents using three deterministic rules:

1. **Same request_id** - Events sharing a request ID
2. **Same service within time window** - Events from the same service within 10 minutes of incident start
3. **Same environment during incident** - Events in the same environment during an active incident

All correlations are explainable and auditable through the `incident_events` table.

### Viewing Incidents

**Web Interface**

Navigate to http://localhost:3000 to:
- View all incidents
- Filter by status (open/resolved)
- Click into incident details
- Examine event timelines
- Read root cause summaries

**API**

```bash
# List all incidents
curl http://localhost:8000/incidents

# Get incident details
curl http://localhost:8000/incidents/1

# Resolve an incident
curl -X PATCH http://localhost:8000/incidents/1/resolve
```

## API Reference

Complete API documentation is available at `/docs` when running the backend:

```
http://localhost:8000/docs
```

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | / | Health check |
| POST | /events | Ingest new event |
| GET | /events | List events with optional filters |
| GET | /incidents | List all incidents |
| GET | /incidents/{id} | Get incident details with timeline |
| PATCH | /incidents/{id}/resolve | Mark incident as resolved |

## Configuration

### Backend Configuration

**Database Connection**

Set via environment variable:
```bash
DATABASE_URL=postgresql://user:password@host:port/database
```

**Correlation Parameters**

Edit `backend/correlation.py`:
```python
ERROR_THRESHOLD = 5              # Errors to trigger incident
TIME_WINDOW_MINUTES = 3          # Rolling detection window
CORRELATION_WINDOW_MINUTES = 10  # Event correlation window
```

### Frontend Configuration

**API Base URL**

Option 1: Environment variable
```bash
VITE_API_URL=https://api.example.com
```

Option 2: Direct configuration in `frontend/src/services/api.js`
```javascript
const API_BASE_URL = 'https://api.example.com';
```

## Project Structure

```
blackbox/
├── backend/
│   ├── main.py              # FastAPI application and routes
│   ├── models.py            # SQLAlchemy database models
│   ├── database.py          # Database configuration
│   ├── correlation.py       # Correlation engine
│   ├── schemas.py           # Pydantic request/response models
│   ├── requirements.txt     # Python dependencies
│   └── Dockerfile           # Backend container config
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── IncidentsList.jsx    # Incidents list view
│   │   │   └── IncidentDetail.jsx   # Incident detail view
│   │   ├── services/
│   │   │   └── api.js       # API client
│   │   ├── App.jsx          # Root component
│   │   └── main.jsx         # Application entry point
│   ├── package.json         # Node dependencies
│   ├── vite.config.js       # Vite configuration
│   └── Dockerfile           # Frontend container config
├── database/
│   └── generate_sample_data.py  # Sample data generator
├── docs/
│   ├── API.md              # API documentation
│   └── DEPLOYMENT.md       # Deployment guide
├── docker-compose.yml      # Multi-service orchestration
└── README.md              # This file
```

## Development

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Code Style

**Python**
- Follow PEP 8 style guide
- Use type hints where applicable
- Maximum line length: 100 characters

**JavaScript**
- Follow Airbnb JavaScript Style Guide
- Use ES6+ features
- Prefer functional components in React

### Database Migrations

```bash
cd backend
alembic revision --autogenerate -m "Description of changes"
alembic upgrade head
```

## Deployment

### Render.com (Recommended)

**1. Create PostgreSQL database**
- New → PostgreSQL
- Note the Internal Database URL

**2. Deploy backend**
- New → Web Service
- Connect GitHub repository
- Root Directory: `backend`
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Environment Variable: `DATABASE_URL` (from step 1)

**3. Deploy frontend**
- New → Static Site
- Connect GitHub repository
- Root Directory: `frontend`
- Build Command: `npm install && npm run build`
- Publish Directory: `dist`
- Environment Variable: `VITE_API_URL` (backend URL from step 2)

Full deployment instructions: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)

### Other Platforms

BLACKBOX can be deployed on:
- Heroku
- AWS (EC2, ECS, or Lambda)
- Google Cloud Platform
- Azure
- DigitalOcean
- Self-hosted infrastructure

## Performance Considerations

**Database Indexing**

Critical indexes are created automatically:
- `events(service, timestamp)`
- `events(request_id)`
- `events(environment, timestamp)`
- `incidents(primary_service, environment, status)`

**Connection Pooling**

Configure in `backend/database.py`:
```python
engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10
)
```

**Frontend Optimization**

- Code splitting via Vite
- Lazy loading of routes
- Memoization of expensive computations

## Limitations and Known Issues

**Current Limitations**

- No authentication or authorization (v1.0)
- Single-tenant only
- No real-time updates (requires page refresh)
- Limited to text-based events (no binary data)

**Planned Features**

See [ROADMAP.md](ROADMAP.md) for planned enhancements.

## Contributing

Contributions are welcome. Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please ensure:
- Code follows style guidelines
- Tests pass
- Documentation is updated
- Commit messages are clear

## Design Decisions

### Why Rule-Based Correlation?

Traditional ML-based approaches lack explainability, which is critical during incident response. Engineers must trust the correlation logic. Rule-based correlation is:
- Deterministic
- Debuggable
- Auditable
- Predictable

### Why Immutable Events?

Events are never updated or deleted to:
- Build trust in the data layer
- Maintain clear audit trails
- Prevent retroactive manipulation
- Enable event sourcing patterns

### Why No AI/ML?

This is a deliberate choice:
- Explainability over cleverness
- No hidden heuristics
- Deterministic behavior
- Provable correctness

### Why Minimal UI?

Incident response happens under stress. The interface is designed to:
- Reduce cognitive load
- Present information sequentially
- Avoid visual noise
- Focus on clarity

## Related Projects

- **Grafana** - Metrics visualization
- **Prometheus** - Metrics collection
- **Jaeger** - Distributed tracing
- **Elasticsearch/Kibana** - Log aggregation
- **PagerDuty** - Incident alerting

BLACKBOX complements these tools by focusing on post-incident analysis and timeline reconstruction.

## License

MIT License

Copyright (c) 2026 Dharsh

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Authors

**Dharsh** - Initial work - [darshhv](https://github.com/darshhv)

## Acknowledgments

Built with the philosophy that calm systems produce calm engineers. Inspired by the challenges of debugging distributed systems in production environments.

## Support

For questions, issues, or suggestions:
- Open an issue on GitHub
- Email: dharsxn46@gmail.com
- Documentation: [docs/](docs/)

## Citation

If you use BLACKBOX in your research or project, please cite:

```
@software{blackbox2026,
  author = {Dharsh},
  title = {BLACKBOX: Incident Reasoning Platform},
  year = {2026},
  url = {https://github.com/darshhv/blackbox}
}
```
