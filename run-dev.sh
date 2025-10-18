#!/bin/bash
echo "🚀 Starting DEVELOPMENT environment..."
docker compose down
docker compose up -d --build
echo "⏳ Waiting for services..."
sleep 15
docker compose exec api alembic upgrade head
docker compose exec api python scripts/seed.py
echo "✅ Development ready at https://branchloans.com"
