#!/bin/bash
echo "🚀 Starting application with monitoring stack..."
docker compose -f docker-compose.yml -f docker-compose.monitoring.yml down
docker compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d --build
echo "⏳ Waiting for services to be ready..."
sleep 20
docker compose exec api alembic upgrade head
docker compose exec api python scripts/seed.py
echo ""
echo "✅ Application ready!"
echo "API: https://branchloans.com/health"
echo "Metrics: https://branchloans.com/metrics"
echo "Prometheus: http://localhost:9090"
echo "Grafana: http://localhost:3000 (admin/admin)"
