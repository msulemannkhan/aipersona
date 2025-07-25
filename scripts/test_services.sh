#!/bin/bash

# Stop any existing containers
docker compose down

# Remove existing volumes to start fresh
docker volume rm ai-soul-entity_chroma-data || true

# Start the services
docker compose up -d

# Function to check service health
check_service() {
    local service=$1
    local max_attempts=30
    local attempt=1

    echo "Checking $service health..."
    while [ $attempt -le $max_attempts ]; do
        if docker compose ps $service | grep -q "healthy"; then
            echo "$service is healthy!"
            return 0
        fi
        echo "Attempt $attempt/$max_attempts: $service is not healthy yet..."
        attempt=$((attempt + 1))
        sleep 5
    done
    echo "$service failed to become healthy"
    return 1
}

# Check services health
check_service db || exit 1
check_service chroma || exit 1
check_service backend || exit 1

echo "All services are healthy!"

# Show logs if any service failed
if [ $? -ne 0 ]; then
    echo "Service check failed. Showing logs..."
    docker compose logs
    exit 1
fi

echo "Services started successfully!" 