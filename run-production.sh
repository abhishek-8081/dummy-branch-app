#!/bin/bash
echo "🚀 Starting PRODUCTION environment..."
docker compose -f docker-compose.yml -f docker-compose.production.yml down
docker compose -f docker-compose.yml -f docker-compose.production.yml up -d --build
echo "⏳ Waiting for services..."
sleep 15
docker compose -f docker-compose.yml -f docker-compose.production.yml exec api alembic upgrade head
echo "✅ Production ready at https://branchloans.com"
