# BLACKBOX Deployment Guide

## Table of Contents
1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [Production Deployment](#production-deployment)
4. [Configuration](#configuration)
5. [Monitoring](#monitoring)
6. [Troubleshooting](#troubleshooting)

---

## Local Development

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+

### Step 1: Database Setup

```bash
# Create database and user
sudo -u postgres psql
```

```sql
CREATE DATABASE blackbox;
CREATE USER blackbox WITH PASSWORD 'blackbox';
GRANT ALL PRIVILEGES ON DATABASE blackbox TO blackbox;
\q
```

### Step 2: Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set database URL (optional)
export DATABASE_URL=postgresql://blackbox:blackbox@localhost:5432/blackbox

# Run backend
python main.py
```

Backend will be available at `http://localhost:8000`

### Step 3: Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend will be available at `http://localhost:3000`

### Step 4: Generate Sample Data

```bash
cd database
python generate_sample_data.py
```

---

## Docker Deployment

### Quick Start

```bash
# Start all services
docker-compose up

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Services
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432

### Accessing Containers

```bash
# Backend shell
docker-compose exec backend bash

# Database shell
docker-compose exec db psql -U blackbox

# Frontend shell
docker-compose exec frontend sh
```

---

## Production Deployment

### Option 1: Single Server with Docker

#### 1. Prepare Server
```bash
# Install Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 2. Configure Environment
```bash
# Create production environment file
cat > .env.prod << EOF
DATABASE_URL=postgresql://blackbox:STRONG_PASSWORD_HERE@db:5432/blackbox
POSTGRES_PASSWORD=STRONG_PASSWORD_HERE
EOF
```

#### 3. Update docker-compose.yml
```yaml
# Use .env.prod file
env_file:
  - .env.prod

# Add restart policies
restart: unless-stopped
```

#### 4. Deploy
```bash
# Pull and start services
docker-compose -f docker-compose.yml up -d

# Check status
docker-compose ps
```

### Option 2: Manual Deployment

#### Backend Deployment

```bash
# On production server
cd backend

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL=postgresql://blackbox:password@db-host:5432/blackbox
export WORKERS=4

# Run with gunicorn for production
pip install gunicorn
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

#### Frontend Deployment

```bash
cd frontend

# Build production bundle
npm run build

# Serve with nginx or any static file server
# The build output is in dist/
```

#### Database Setup

```bash
# Create production database
sudo -u postgres psql
```

```sql
CREATE DATABASE blackbox;
CREATE USER blackbox WITH PASSWORD 'strong_password_here';
GRANT ALL PRIVILEGES ON DATABASE blackbox TO blackbox;
ALTER DATABASE blackbox OWNER TO blackbox;
```

### Option 3: Cloud Platforms

#### Render.com

1. **Database**:
   - Create PostgreSQL instance
   - Note connection URL

2. **Backend**:
   - Create Web Service from Git
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Add environment variable: `DATABASE_URL`

3. **Frontend**:
   - Create Static Site from Git
   - Build command: `npm install && npm run build`
   - Publish directory: `dist`

#### Heroku

```bash
# Install Heroku CLI
# Login
heroku login

# Create app
heroku create blackbox-app

# Add PostgreSQL
heroku addons:create heroku-postgresql:mini

# Deploy backend
git push heroku main

# Deploy frontend separately or use buildpack
```

---

## Configuration

### Backend Configuration

```python
# correlation.py - Incident detection thresholds
ERROR_THRESHOLD = 5              # Errors to trigger incident
TIME_WINDOW_MINUTES = 3          # Rolling detection window
CORRELATION_WINDOW_MINUTES = 10  # Event correlation window
```

### Database Configuration

```python
# database.py
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://blackbox:blackbox@localhost:5432/blackbox"
)
```

### Frontend Configuration

```javascript
// vite.config.js - API proxy
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true,
  }
}
```

---

## Monitoring

### Health Checks

```bash
# Backend health
curl http://localhost:8000/

# Expected response:
# {"service":"BLACKBOX","status":"operational","purpose":"incident reasoning platform"}
```

### Database Monitoring

```sql
-- Check event count
SELECT COUNT(*) FROM events;

-- Check incident count
SELECT COUNT(*) FROM incidents;

-- Recent incidents
SELECT id, primary_service, status, start_time 
FROM incidents 
ORDER BY start_time DESC 
LIMIT 10;

-- Events per service
SELECT service, COUNT(*) as event_count
FROM events
GROUP BY service
ORDER BY event_count DESC;
```

### Docker Monitoring

```bash
# Container status
docker-compose ps

# Resource usage
docker stats

# Logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
```

---

## Troubleshooting

### Backend Won't Start

**Issue**: Database connection error

```bash
# Check if PostgreSQL is running
docker-compose ps db

# Check database logs
docker-compose logs db

# Verify connection string
echo $DATABASE_URL

# Test connection manually
psql postgresql://blackbox:blackbox@localhost:5432/blackbox
```

**Issue**: Port 8000 already in use

```bash
# Find process using port
lsof -i :8000

# Kill process or use different port
uvicorn main:app --port 8001
```

### Frontend Won't Connect to Backend

**Issue**: CORS errors

```python
# In main.py, verify CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Issue**: API proxy not working

```javascript
// vite.config.js - Check proxy configuration
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    }
  }
}
```

### Database Issues

**Issue**: Tables not created

```bash
# Connect to database
docker-compose exec db psql -U blackbox

# Check if tables exist
\dt

# If not, restart backend to trigger init_db()
docker-compose restart backend
```

**Issue**: Slow queries

```sql
-- Add indexes if needed
CREATE INDEX idx_events_timestamp ON events(timestamp);
CREATE INDEX idx_events_service ON events(service);
CREATE INDEX idx_events_request_id ON events(request_id);
```

### Docker Issues

**Issue**: Containers won't start

```bash
# Remove and rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up
```

**Issue**: Database data lost

```bash
# Check volume
docker volume ls

# Backup volume
docker run --rm -v blackbox_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/db-backup.tar.gz /data
```

---

## Backup and Recovery

### Database Backup

```bash
# Backup database
docker-compose exec db pg_dump -U blackbox blackbox > backup.sql

# Restore database
docker-compose exec -T db psql -U blackbox blackbox < backup.sql
```

### Full System Backup

```bash
# Stop services
docker-compose down

# Backup volumes
docker run --rm -v blackbox_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres-data.tar.gz /data

# Restart services
docker-compose up -d
```

---

## Performance Tuning

### Database

```sql
-- PostgreSQL configuration for better performance
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
```

### Backend

```bash
# Run with multiple workers for production
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120
```

### Frontend

```bash
# Build optimized production bundle
npm run build

# Serve with nginx for best performance
```

---

## Security Checklist

- [ ] Change default database password
- [ ] Use HTTPS in production
- [ ] Set proper CORS origins (not `*`)
- [ ] Enable database SSL connections
- [ ] Set up proper firewall rules
- [ ] Regular security updates
- [ ] Implement rate limiting
- [ ] Add authentication (future enhancement)

---

## Next Steps

After deployment:

1. Send test events to verify ingestion
2. Check incident detection works correctly
3. Verify timeline rendering is accurate
4. Monitor database growth
5. Set up regular backups
6. Configure log retention policies

---

For more information, see the main [README.md](../README.md)
