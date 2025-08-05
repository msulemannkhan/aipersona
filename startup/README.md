# AI Persona Startup Scripts

This directory contains enhanced startup scripts that automate the complete setup process for the AI Persona project with robust error handling and fallback mechanisms.

## Quick Start

### For Mac/Linux:
```bash
./startup/startup.sh
```

### For Windows:
```cmd
startup\startup.bat
```

## Features

### 🚀 **Automated Setup**
- Creates Docker network automatically
- Builds required Docker images
- Starts all services in correct order
- Creates test users and AI souls
- Validates service health

### 🔧 **Enhanced Error Handling**
- **Dynamic Container Detection**: Automatically finds backend container regardless of naming conventions
- **Health Check Validation**: Waits for backend API to be fully responsive
- **Fallback Mechanisms**: Multiple strategies for container discovery
- **Graceful Degradation**: Continues setup even if some steps fail
- **Detailed Logging**: Shows container status, logs, and debugging information

### 🛠 **Improved Logging**
- Color-coded output for better visibility
- Progress indicators during long operations
- Container status monitoring
- Detailed error messages with troubleshooting suggestions

### ⚡ **Platform Support**
- Cross-platform compatibility (Mac, Linux, Windows)
- OS-specific optimizations and warnings
- Automatic platform detection

## What the Scripts Do

### Step 1: Environment Validation
- Checks Docker and Docker Compose installation
- Verifies Docker daemon is running
- Validates project directory structure

### Step 2: Network Creation
- Creates `spiritual-chatbot-traefik-public` network
- Skips if network already exists
- Provides clear status messages

### Step 3: Image Building
- Builds `prestart` and `frontend` Docker images
- Shows build progress and logs
- Handles build failures gracefully

### Step 4: Service Startup
- Starts all Docker Compose services
- Monitors container status
- Displays container information table

### Step 5: Backend Health Check
- **Smart Container Detection**: Finds backend container using multiple strategies:
  - Project-based naming (`projectname-backend-1`)
  - Underscore naming (`projectname_backend_1`)
  - Generic naming (`backend-1`)
  - Fallback search for any container with "backend" in the name

- **Health Validation**: 
  - Verifies container is running
  - Checks API health endpoint (`/api/utils/health-check/`)
  - Shows progress indicators
  - Displays recent logs for debugging

### Step 6: User Setup
- Creates test users using detected backend container
- Handles execution failures gracefully
- Provides fallback options

### Step 7: AI Souls Creation
- Adds test AI souls for admin user
- Uses dynamic container detection
- Continues even if this step fails

## Error Handling Features

### Container Detection Failures
- **Problem**: Backend container not found
- **Solution**: Multiple naming strategies + fallback search
- **Fallback**: Manual container name input option

### Backend Health Check Failures
- **Problem**: Backend API not responding
- **Solution**: Extended wait time with progress indicators
- **Fallback**: Option to continue setup manually

### Command Execution Failures
- **Problem**: Docker exec commands fail
- **Solution**: Detailed error messages + troubleshooting steps
- **Fallback**: Skip failed steps and continue

### Network Issues
- **Problem**: Docker network creation fails
- **Solution**: Check for existing network first
- **Fallback**: Continue with existing network

## Troubleshooting

### Common Issues and Solutions

#### 1. Container Not Found
```
[ERROR] Backend container not found after 60 attempts
```
**Solution**: Script will show available containers and try fallback detection. You can also manually check:
```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

#### 2. Backend Health Check Timeout
```
[ERROR] Backend container did not become healthy within expected time
```
**Solution**: Script shows recent logs and offers to continue manually. Check backend logs:
```bash
docker logs [container-name] --tail=20
```

#### 3. Build Failures
```
[ERROR] Building prestart and frontend images failed
```
**Solution**: Check Docker daemon and disk space. The script will show build logs for debugging.

#### 4. Network Already Exists
```
[WARNING] Network 'spiritual-chatbot-traefik-public' already exists, skipping creation
```
**Solution**: This is normal and expected. The script continues automatically.

### Manual Recovery Commands

If the script fails, you can run these commands manually:

```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs backend

# Restart services
docker-compose restart backend

# Reset everything
docker-compose down && docker-compose up -d

# Create users manually (replace container name)
docker exec -it [backend-container-name] python /app/scripts/docker_reset_users.py
```

## Advanced Usage

### Environment Variables
The scripts respect the following environment variables:
- `COMPOSE_PROJECT_NAME`: Override project name for container naming
- `DOCKER_TIMEOUT`: Override default timeout values

### Debug Mode
For additional debugging information:
```bash
# Mac/Linux
DEBUG=1 ./startup/startup.sh

# Windows
set DEBUG=1 && startup\startup.bat
```

### Custom Container Names
If you're using custom container names, the script will:
1. Try standard naming patterns
2. Search for containers with "backend" in the name
3. Ask for manual input if needed

## Script Architecture

### Bash Script (startup.sh)
- **Functions**: Modular design with reusable functions
- **Error Handling**: `set -e` for fail-fast behavior
- **Logging**: Color-coded output with status levels
- **Cleanup**: Automatic cleanup of temporary files

### Batch Script (startup.bat)
- **Functions**: Goto-based function simulation
- **Error Handling**: Error level checking after each command
- **Logging**: Windows-compatible color output
- **Cleanup**: Automatic temp file cleanup

## Default Credentials

After successful setup, use these credentials:

**Admin User:**
- Email: `admin@example.com`
- Password: `TestPass123!`

**Application URLs:**
- Frontend: http://localhost:19100
- Backend API: http://localhost:17010
- API Documentation: http://localhost:17010/docs

## Contributing

When modifying the scripts:

1. Test on both Mac/Linux and Windows
2. Update this README with new features
3. Ensure error handling is comprehensive
4. Add progress indicators for long operations
5. Include troubleshooting information

## Version History

- **v2.0**: Enhanced error handling and dynamic container detection
- **v1.0**: Basic sequential command execution

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Run with debug mode enabled
3. Check Docker daemon status
4. Verify project directory structure
5. Review container logs for specific errors 