# Branch Loan API - Production-Ready Deployment

A containerized microloans REST API built with Flask, PostgreSQL, SQLAlchemy, and Alembic, deployed with Docker and automated CI/CD.

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
└──────────────┘     └─────────────┘
```

**Components:**
- **Nginx:** Handles HTTPS, SSL termination, and reverse proxy
- **Flask API:** REST API with Gunicorn WSGI server
- **PostgreSQL:** Relational database for loan data
- **Docker:** Containerization for consistent deployments

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
| GET | `/health` | Health check |
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

### Check Logs
```bash
docker compose logs api -f
docker compose logs nginx -f
docker compose logs db -f
```

## 🔧 Environment Variables

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

## Future Improvements

- Add Kubernetes deployment manifests
- Implement comprehensive test suite
- Add Prometheus + Grafana for monitoring
- Implement API authentication (JWT)
- Add rate limiting with Redis
- Database backup automation

## Development Commands

```bash
# Start services
docker compose up -d

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

**Time Spent:** Approximately 5 hours
