# How to Run AI Persona Project

## Prerequisites
- Docker installed on your system
- Git installed on your system
- Ensure you have a `.env` file in the project root

## Quick Start (3 Steps)

### 1. Clone and Navigate
```bash
git clone <repository-url>
cd ai-persona
```

### 2. Build and Start Services
```bash
# Create required network
docker network create spiritual-chatbot-traefik-public

# Build and start all services
docker-compose up --build
```

### 3. Create Test Users and AI Souls
```bash
# Create test users
docker exec -it ai-persona-backend-1 python /app/scripts/docker_reset_users.py

# Create AI souls
docker exec -it ai-persona-backend-1 python /app/scripts/add_test_ai_souls.py admin@example.com
```

## Access the Application

- **Frontend**: http://localhost:19100
- **Backend API**: http://localhost:17010
- **API Documentation**: http://localhost:17010/docs

## Test Users (Password: TestPass123!)

- **Admin**: admin@example.com
- **Counselor**: counselor@example.com
- **Trainer**: trainer@example.com
- **User**: user@example.com

## AI Souls Available

1. **Therapy Assistant** - Mental health support
2. **Spiritual Guide** - Spiritual guidance and wisdom
3. **Life Coach** - Goal setting and motivation
4. **Emotional Support** - Emotional intelligence and empathy
5. **Wisdom Teacher** - Philosophy and life lessons
6. **Creative Muse** - Creativity and artistic inspiration

## Docker Images Overview

### Core Application Images (Built from Source)
- **backend:latest** - FastAPI Python application with AI services
- **frontend:latest** - React/Vite application with modern UI

### External Service Images
- **postgres:17** - PostgreSQL database for data storage
- **redis:7-alpine** - Redis cache for session management
- **qdrant/qdrant:latest** - Vector database for Enhanced RAG
- **adminer** - Database management web interface
- **traefik:3.0** - Reverse proxy and load balancer
- **schickling/mailcatcher** - Email testing service

## Port Configuration Details

### Why Custom Ports (17000-19000 range)?
- Avoids conflicts with common services (MySQL 3306, PostgreSQL 5432, etc.)
- Allows multiple projects on same system
- Prevents interference with system services
- Suitable for AWS EC2 multi-container deployments

### Port Mapping Table

| Service | External Port | Internal Port | Protocol | Purpose |
|---------|---------------|---------------|----------|---------|
| **Frontend** | 19100 | 5173 | HTTP | React development server |
| **Frontend (Prod)** | 19101 | 80 | HTTP | Production frontend |
| **Backend API** | 17010 | 8000 | HTTP | FastAPI backend |
| **Database** | 17432 | 5432 | TCP | PostgreSQL database |
| **Admin Panel** | 17080 | 8080 | HTTP | Adminer database UI |
| **Redis** | 17379 | 6379 | TCP | Redis cache |
| **Qdrant HTTP** | 17333 | 6333 | HTTP | Vector database API |
| **Qdrant gRPC** | 17334 | 6334 | gRPC | Vector database protocol |
| **Flower** | 17555 | 5555 | HTTP | Celery task monitoring |
| **Traefik Proxy** | 17801 | 80 | HTTP | Reverse proxy |
| **Traefik Dashboard** | 17890 | 8080 | HTTP | Proxy management |
| **Mailcatcher HTTP** | 18080 | 1080 | HTTP | Email web interface |
| **Mailcatcher SMTP** | 18025 | 1025 | SMTP | Email testing |

### Service Access URLs

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:19100 | Main application |
| Backend API | http://localhost:17010 | API endpoints |
| API Docs | http://localhost:17010/docs | Swagger documentation |
| Database Admin | http://localhost:17080 | Database management |
| Task Monitor | http://localhost:17555 | Celery monitoring |
| Proxy Dashboard | http://localhost:17890 | Traefik dashboard |
| Email Testing | http://localhost:18080 | Mailcatcher interface |

## Common Commands

```bash
# Stop all services
docker-compose down

# View service logs
docker-compose logs -f

# Check container status
docker ps

# Restart specific service
docker-compose restart backend

# View specific service logs
docker-compose logs -f backend

# Reset database (removes all data)
docker-compose down -v

# Check prestart service logs (runs once and exits)
docker logs aipersona-prestart-1
```

## Important Notes

- The **prestart service** runs database migrations and initial data setup, then exits normally (exit code 0)
- If prestart shows exit code 1, check its logs for database connection or migration errors
- All other services should remain running continuously

## Troubleshooting

1. **Port conflicts**: All ports use 17000-19000 range to avoid conflicts
2. **Database issues**: Run `docker-compose down -v` to reset volumes
3. **Permission errors**: Run `chmod +x backend/scripts/*.py`
4. **Build issues**: Run `docker-compose build --no-cache`
5. **Docker naming conflicts**: If you see "image already exists" errors:
   ```bash
   docker-compose down --volumes --remove-orphans
   docker system prune -f
   docker network create spiritual-chatbot-traefik-public
   docker-compose up --build
   ```
6. **Missing network**: If you get "network not found" errors:
   ```bash
   docker network create spiritual-chatbot-traefik-public
   ```
7. **Prestart service failure**: If you get "prestart didn't complete successfully" errors:
   ```bash
   # Check the prestart service logs
   docker logs aipersona-prestart-1
   
   # If it shows database connection errors, wait for database to be ready
   # If it shows migration errors, reset the database:
   docker-compose down -v
   docker-compose up --build
   
   # The prestart service should exit with code 0 (success) after running migrations
   # Check the actual exit code:
   docker ps -a --filter "name=prestart" --format "table {{.Names}}\t{{.Status}}"
   ```

## Development Mode

For development with hot-reload:
```bash
docker-compose -f docker-compose.yml -f docker-compose.override.yml up --build
```

## Production Deployment

For production on AWS EC2:
1. All services use custom ports (17000-19000)
2. Configure security groups to allow these ports
3. Use production docker-compose file
4. Set up SSL certificates with Traefik

That's it! The system is now ready to use.
