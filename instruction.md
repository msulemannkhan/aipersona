# Instructions to Run AI Persona Project

## Quick Start (Recommended)

### Using the Automated Startup Script

For the easiest setup experience, use the automated startup script that handles all the setup steps:

**For Mac/Linux:**
```bash
git clone <repository-url>
cd ai-persona
./startup/startup.sh
```

**For Windows:**
```cmd
git clone <repository-url>
cd ai-persona
startup\startup.bat
```

The script will:
- Detect your operating system
- Check Docker installation and status
- Guide you through the setup process
- Run all commands in the correct order with proper logging
- Handle errors gracefully with helpful messages
- Wait for services to be ready before proceeding

After the script completes, access the application at http://localhost:19100.

**Default login credentials:**
- Email: admin@example.com
- Password: changethis

## Manual Setup (Alternative)

If you prefer to run the commands manually or encounter issues with the automated script:

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

## Troubleshooting

If you encounter issues:

1. **Docker not running**: Make sure Docker Desktop is running
2. **Permission denied**: On Linux/Mac, ensure the script is executable: `chmod +x startup/startup.sh`
3. **Network already exists**: The script will skip network creation if it already exists
4. **Container not ready**: The script waits for the backend container to be ready before proceeding
5. **Windows issues**: Try running the batch script as Administrator

## Additional Commands

- **View logs**: `docker-compose logs -f`
- **Stop services**: `docker-compose down`
- **Restart services**: `docker-compose restart`
