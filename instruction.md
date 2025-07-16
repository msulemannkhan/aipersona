# Instructions to Run AI Persona Project

## Quick Start

### 1. Clone and Navigate

Clone the repository and navigate to the project directory:

```bash
git clone <repository-url>
cd ai-persona
```

### 2. Build and Start Services

Build the necessary images and start the services:

```bash
docker network create spiritual-chatbot-traefik-public
docker-compose build prestart frontend
docker-compose up -d
```

### 3. Create Test Users and AI Souls

Create test users and AI souls using the following commands:

```bash
docker exec -it ai-persona-backend-1 python /app/scripts/docker_reset_users.py
docker exec -it ai-persona-backend-1 python /app/scripts/add_test_ai_souls.py admin@example.com
```

After completing these steps, access the application at http://localhost:19100.
