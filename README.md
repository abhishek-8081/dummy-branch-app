# Branch Loan API - Production-Ready Deployment

A containerized microloans REST API built with Flask, PostgreSQL, SQLAlchemy, and Alembic, deployed with Docker and automated CI/CD. Includes comprehensive monitoring and observability features.

## Architecture

```
┌──────────────┐
│   Browser    │
└──────┬───────┘
       │ HTTPS (443)
       ▼
┌──────────────┐
│    Nginx     │ (SSL Termination)
└──────┬───────┘
       │ HTTP (8000)
       ▼
┌──────────────┐     ┌─────────────┐
│  Flask API   │────▶│ PostgreSQL  │
│  (Gunicorn)  │     │   Database  │
└──────┬───────┘     └─────────────┘
       │
       │ Metrics (Scraping)
       ▼
┌──────────────┐     ┌─────────────┐
│  Prometheus  │────▶│   Grafana   │
└──────────────┘     └─────────────┘
```

**Components:**
- **Nginx:** Handles HTTPS, SSL termination, and reverse proxy
- **Flask API:** REST API with Gunicorn WSGI server
- **PostgreSQL:** Relational database for loan data
- **Docker:** Containerization for consistent deployments
- **Prometheus:** Metrics collection and monitoring
- **Grafana:** Metrics visualization and dashboards

## Quick Start

### Prerequisites
- Docker Desktop (with WSL2 for Windows users)
- Git
- 8GB RAM minimum

### Local Development Setup

**1. Clone the repository:**
```bash
git clone https://github.com/abhishek-8081/dummy-branch-app
cd dummy-branch-app
```

**2. Set up local domain:**

**On Linux/WSL/Mac:**
```bash
sudo nano /etc/hosts
```

**On Windows (as Administrator):**
Edit: `C:\Windows\System32\drivers\etc\hosts`

Add this line:
```
127.0.0.1 branchloans.com
```

For Windows WSL users, use your WSL IP instead:
```
YOUR_WSL_IP branchloans.com
```

To find your WSL IP:
```bash
hostname -I | awk '{print $1}'
```

**3. Generate SSL certificates:**
```bash
mkdir certs
openssl req -x509 -newkey rsa:4096 -keyout certs/key.pem -out certs/cert.pem -days 365 -nodes -subj "/CN=branchloans.com"
```

**4. Start development environment:**
```bash
chmod +x run-dev.sh
./run-dev.sh
```

**5. Access the API:**
- Browser: `https://branchloans.com/health` (accept security warning for self-signed cert)
- Curl: `curl -k https://branchloans.com/health`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Enhanced health check with DB verification |
| GET | `/metrics` | Prometheus metrics endpoint |
| GET | `/api/loans` | List all loans |
| GET | `/api/loans/:id` | Get specific loan |
| POST | `/api/loans` | Create new loan |
| GET | `/api/stats` | Loan statistics |

### Example: Create a New Loan
```bash
curl -k -X POST https://branchloans.com/api/loans \
  -H 'Content-Type: application/json' \
  -d '{
    "borrower_id": "usr_india_001",
    "amount": 15000,
    "currency": "INR",
    "term_months": 12,
    "interest_rate_apr": 18.0
  }'
```

## Multi-Environment Setup

### Development Environment
```bash
./run-dev.sh
```
- Debug logging enabled
- Small resource limits
- Database: `microloans_dev`

### Staging Environment
```bash
./run-staging.sh
```
- Standard logging
- Medium resource limits
- Database: `microloans_staging`

### Production Environment
```bash
./run-production.sh
```
- Warning-level logging only
- High resource limits
- Auto-restart on failure
- Database: `microloans_prod`

## Monitoring and Observability

### Enhanced Health Check
The `/health` endpoint verifies both API and database connectivity:

```bash
curl -k https://branchloans.com/health
```

**Response:**
```json
{
  "status": "healthy",
  "checks": {
    "api": "ok",
    "database": "ok"
  }
}
```

If database is down:
```json
{
  "status": "unhealthy",
  "checks": {
    "api": "ok",
    "database": "failed"
  },
  "error": "connection error details"
}
```

### Structured JSON Logging
All application logs are in JSON format with rich context:

```bash
docker compose logs api --tail=20
```

**Log Entry Example:**
```json
{
  "timestamp": "2025-10-18 04:01:10",
  "level": "INFO",
  "name": "app",
  "message": "GET /health 200",
  "duration_ms": 20.16,
  "status_code": 200,
  "logger": "app",
  "request_id": "N/A",
  "method": "GET",
  "path": "/health",
  "remote_addr": "172.19.0.5",
  "environment": "development"
}
```

### Prometheus Metrics
Application exposes Prometheus-compatible metrics at `/metrics`:

```bash
curl -k https://branchloans.com/metrics
```

**Available Metrics:**
- `loan_api_requests_total` - Total number of API requests (labeled by method, endpoint, status)
- `loan_api_request_duration_seconds` - Request duration histogram
- `loan_api_total_loans` - Current number of loans in database
- `loan_api_total_amount` - Total loan amount across all loans
- `loan_api_database_connections` - Active database connections

### Running with Monitoring Stack

**Start with monitoring (Prometheus + Grafana):**
```bash
./run-with-monitoring.sh
```

**Or manually:**
```bash
docker compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d --build
```

**Access monitoring tools:**
- **Prometheus UI:** http://localhost:9090
- **Grafana:** http://localhost:3000
  - Username: `admin`
  - Password: `admin`

### Prometheus Query Examples

Try these queries in Prometheus UI:

```promql
# Request rate per minute
rate(loan_api_requests_total[1m])

# Average request duration (in seconds)
rate(loan_api_request_duration_seconds_sum[5m]) / rate(loan_api_request_duration_seconds_count[5m])

# Total loans in database
loan_api_total_loans

# Total loan amount
loan_api_total_amount

# Active database connections
loan_api_database_connections

# Error rate
rate(loan_api_requests_total{status=~"5.."}[5m])
```

### Grafana Setup

After logging into Grafana (http://localhost:3000):

1. Prometheus is already configured as a data source
2. Click "Explore" (compass icon on left sidebar)
3. Select "Prometheus" as data source
4. Enter queries from examples above
5. Create custom dashboards by clicking "+" → "Dashboard"

**Recommended Dashboard Panels:**
- Request rate over time (graph)
- Total loans (stat)
- Total loan amount (stat)
- Request duration p95 (graph)
- Database connections (gauge)

## CI/CD Pipeline

### Pipeline Stages
```
TEST → BUILD → SECURITY SCAN → PUSH TO REGISTRY
```

**1. Test Stage**
- Runs database migrations
- Executes pytest tests

**2. Build Stage**
- Builds Docker image
- Tags with git commit SHA

**3. Security Scan Stage**
- Scans with Trivy for vulnerabilities
- Uploads results to GitHub Security

**4. Push Stage**
- Pushes to GitHub Container Registry
- Only runs on main branch

### Triggers
- **Push to main:** Full pipeline (all 4 stages)
- **Pull Request:** Test, Build, and Scan only

### View Pipeline
`https://github.com/abhishek-8081/dummy-branch-app/actions`

### Pull Published Image
```bash
docker pull ghcr.io/abhishek-8081/dummy-branch-app:latest
```

## Troubleshooting

### Cannot access branchloans.com
**Solution:** 
- Check hosts file has correct entry
- On Windows WSL: Use WSL IP (not 127.0.0.1)
- Flush DNS: `ipconfig /flushdns` (Windows) or `sudo systemd-resolve --flush-caches` (Linux)

### SSL Certificate Warning
**Expected behavior** - self-signed certificate for local development
- Click "Advanced" → "Proceed to branchloans.com"
- Or use `curl -k` flag to skip verification

### Database Connection Failed
```bash
docker compose down -v
docker compose up -d --build
sleep 15
docker compose exec api alembic upgrade head
docker compose exec api python scripts/seed.py
```

### Prometheus Not Scraping Metrics
```bash
# Check if API is exposing metrics
curl -k https://branchloans.com/metrics

# Check Prometheus logs
docker compose logs prometheus

# Verify Prometheus targets
# Go to http://localhost:9090/targets
```

### Grafana Data Source Not Working
```bash
# Check Prometheus is running
docker compose ps prometheus

# Check Grafana logs
docker compose logs grafana

# Verify data source configuration in Grafana UI
```

### Check Logs
```bash
docker compose logs api -f
docker compose logs nginx -f
docker compose logs db -f
docker compose logs prometheus -f
docker compose logs grafana -f
```

## Environment Variables

| Variable | Development | Staging | Production |
|----------|-------------|---------|------------|
| FLASK_ENV | development | staging | production |
| LOG_LEVEL | DEBUG | INFO | WARNING |
| DB_POOL_SIZE | 5 | 10 | 20 |

## Design Decisions

### Why Nginx for HTTPS?
- Separates SSL termination from application logic
- Better performance for handling TLS
- Industry standard approach

### Why Docker Compose Override Files?
- DRY principle - shared base configuration
- Easy environment switching
- Clear separation of concerns

### Why GitHub Container Registry?
- Free for public repositories
- Integrated with GitHub Actions
- No external service setup

### Why Prometheus + Grafana?
- Industry standard for metrics and monitoring
- Easy Docker deployment
- Rich query language (PromQL)
- Excellent visualization capabilities

## Future Improvements

- Add Kubernetes deployment manifests
- Implement comprehensive test suite
- Add alerting rules in Prometheus
- Implement API authentication (JWT)
- Add rate limiting with Redis
- Database backup automation
- Add Loki for log aggregation
- Implement distributed tracing with Jaeger

## Development Commands

```bash
# Start services (basic)
docker compose up -d

# Start with monitoring
docker compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d

# View logs
docker compose logs -f

# Run migrations
docker compose exec api alembic upgrade head

# Seed database
docker compose exec api python scripts/seed.py

# Stop services
docker compose down

# Clean restart
docker compose down -v
docker compose up -d --build

# Check container status
docker compose ps

# Access database
docker compose exec db psql -U postgres -d microloans
```

## Author

**Abhishek Kumar**
- Email: abhishekrajputji2004@gmail.com
- GitHub: [@abhishek-8081](https://github.com/abhishek-8081)


**Completed Features:**
- Part 1: Containerization with HTTPS
- Part 2: Multi-Environment Setup
- Part 3: CI/CD Pipeline with GitHub Actions
- Part 4: Comprehensive Documentation

**Bonus Features:**
- Enhanced Health Check with Database Verification
- Structured JSON Logging with Request Context
- Prometheus Metrics Endpoint
- Prometheus and Grafana Monitoring Stack

**Time Spent:** Approximately 6 hours