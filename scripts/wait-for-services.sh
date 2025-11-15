#!/bin/bash
echo "Waiting for services to be ready..."

# Wait for PostgreSQL
until docker-compose exec -T postgres pg_isready -U appuser -d appdb; do
    echo "Waiting for PostgreSQL..."
    sleep 2
done

# Wait for MongoDB
until docker-compose exec -T mongodb mongosh --eval "db.adminCommand({ping: 1})" > /dev/null 2>&1; do
    echo "Waiting for MongoDB..."
    sleep 2
done

# Wait for Redis
until docker-compose exec -T redis redis-cli ping | grep -q "PONG"; do
    echo "Waiting for Redis..."
    sleep 2
done

# Wait for RabbitMQ
until docker-compose exec -T rabbitmq rabbitmq-diagnostics -q ping > /dev/null 2>&1; do
    echo "Waiting for RabbitMQ..."
    sleep 2
done

# Wait for Flask API
until curl -f http://localhost:5000/api/health > /dev/null 2>&1; do
    echo "Waiting for Flask API..."
    sleep 2
done

echo "All services are ready!"