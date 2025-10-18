#!/bin/bash
echo "🚀 Starting STAGING environment..."
docker compose -f docker-compose.yml -f docker-compose.staging.yml down
docker compose -f docker-compose.yml -f docker-compose.staging.yml up -d --build
echo "⏳ Waiting for services..."
sleep 15
docker compose -f docker-compose.yml -f docker-compose.staging.yml exec api alembic upgrade head
echo "✅ Staging ready at https://branchloans.com"
