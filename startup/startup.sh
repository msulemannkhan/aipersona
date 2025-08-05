#!/bin/bash

# AI Persona Project Startup Script
# This script automates the complete setup process for the AI Persona project

set -e  # Exit on any error

# Color codes for better output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to run command with logging
run_command() {
    local cmd="$1"
    local description="$2"
    
    print_status "Running: $description"
    echo -e "${BLUE}Command:${NC} $cmd"
    echo "----------------------------------------"
    
    if eval "$cmd"; then
        print_success "$description completed successfully"
        echo ""
    else
        print_error "$description failed"
        echo ""
        return 1
    fi
}

# Function to detect operating system
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "mac"
    elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        echo "windows"
    else
        echo "unknown"
    fi
}

# Function to check if Docker is running
check_docker() {
    print_status "Checking Docker installation and status..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed or not in PATH"
        echo "Please install Docker and try again."
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker is not running"
        echo "Please start Docker and try again."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed or not in PATH"
        echo "Please install Docker Compose and try again."
        exit 1
    fi
    
    print_success "Docker and Docker Compose are ready"
}

# Function to get backend container name dynamically
get_backend_container_name() {
    # Get all running container names
    local running_containers
    running_containers=$(docker ps --filter "status=running" --format "{{.Names}}")
    
    # Try to find backend container with different naming patterns
    local backend_container=""
    
    # Check each running container
    while IFS= read -r container_name; do
        # Skip empty lines
        [[ -z "$container_name" ]] && continue
        
        # Check if it's a backend container
        if [[ "$container_name" == *"backend"* ]]; then
            backend_container="$container_name"
            break
        fi
    done <<< "$running_containers"
    
    if [[ -n "$backend_container" ]]; then
        echo "$backend_container"
        return 0
    fi
    
    return 1
}

# Function to wait for backend container to be ready
wait_for_backend() {
    print_status "Waiting for backend container to be ready..."
    local max_attempts=60
    local attempt=0
    local backend_container=""
    
    # First, try to find the backend container
    while [ $attempt -lt $max_attempts ]; do
        backend_container=$(get_backend_container_name)
        if [[ -n "$backend_container" ]]; then
            print_success "Found backend container: $backend_container"
            break
        fi
        
        echo -n "."
        sleep 2
        ((attempt++))
    done
    
    if [[ -z "$backend_container" ]]; then
        print_error "Backend container not found after $max_attempts attempts"
        print_status "Available containers:"
        docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        
        # Fallback: try to find any running container with backend in the name
        print_status "Trying fallback container detection..."
        local fallback_container
        fallback_container=$(docker ps --format "{{.Names}}" | grep -i backend | head -1)
        if [[ -n "$fallback_container" ]]; then
            print_warning "Using fallback container: $fallback_container"
            backend_container="$fallback_container"
        else
            return 1
        fi
    fi
    
    # Wait for the backend to be healthy
    attempt=0
    print_status "Waiting for backend health check..."
    while [ $attempt -lt $max_attempts ]; do
        # Check if container is running
        if ! docker ps --filter "name=$backend_container" --filter "status=running" | grep -q "$backend_container"; then
            print_error "Backend container $backend_container is not running"
            docker ps --filter "name=$backend_container" --format "table {{.Names}}\t{{.Status}}"
            return 1
        fi
        
        # Check if the API is responding
        if docker exec "$backend_container" curl -f http://localhost:8000/api/utils/health-check/ > /dev/null 2>&1; then
            print_success "Backend container is healthy and ready"
            # Store the container name for later use
            echo "$backend_container" > /tmp/backend_container_name
            return 0
        fi
        
        # Show progress
        if [ $((attempt % 10)) -eq 0 ]; then
            print_status "Still waiting for backend... (attempt $attempt/$max_attempts)"
            # Show container logs for debugging
            print_status "Recent backend logs:"
            docker logs "$backend_container" --tail=5 2>/dev/null || true
        fi
        
        echo -n "."
        sleep 2
        ((attempt++))
    done
    
    print_error "Backend container did not become healthy within expected time"
    print_status "Final container status:"
    docker ps --filter "name=$backend_container" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    
    print_status "Backend container logs (last 20 lines):"
    docker logs "$backend_container" --tail=20 2>/dev/null || true
    
    return 1
}

# Function to execute backend commands with proper container name
execute_backend_command() {
    local command="$1"
    local description="$2"
    
    # Get backend container name
    local backend_container
    if [[ -f /tmp/backend_container_name ]]; then
        backend_container=$(cat /tmp/backend_container_name)
    else
        backend_container=$(get_backend_container_name)
    fi
    
    if [[ -z "$backend_container" ]]; then
        print_error "Cannot find backend container"
        return 1
    fi
    
    print_status "Using backend container: $backend_container"
    run_command "docker exec -it $backend_container $command" "$description"
}

# Main execution
main() {
    echo "=========================================="
    echo "   AI Persona Project Startup Script     "
    echo "=========================================="
    echo ""
    
    # Detect operating system
    OS=$(detect_os)
    print_status "Detected OS: $OS"
    
    # Platform-specific notes
    case $OS in
        "mac")
            print_warning "macOS detected. Make sure Docker Desktop is running."
            ;;
        "windows")
            print_warning "Windows detected. Make sure Docker Desktop is running."
            print_warning "If using Git Bash, some commands might need adjustment."
            ;;
        "linux")
            print_status "Linux detected. Proceeding with standard Docker commands."
            ;;
        *)
            print_warning "Unknown OS detected. Proceeding with standard commands."
            ;;
    esac
    
    # Ask user if they want to continue
    echo ""
    read -p "Do you want to continue with the setup? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status "Setup cancelled by user"
        exit 0
    fi
    
    # Check Docker installation
    check_docker
    
    echo ""
    print_status "Starting AI Persona project setup..."
    echo "This will run the following commands in sequence:"
    echo "1. Create Docker network"
    echo "2. Build Docker images"
    echo "3. Start services"
    echo "4. Reset users"
    echo "5. Add test AI souls"
    echo ""
    
    # Step 1: Create Docker network
    print_status "STEP 1/5: Creating Docker network..."
    if docker network ls | grep -q "spiritual-chatbot-traefik-public"; then
        print_warning "Network 'spiritual-chatbot-traefik-public' already exists, skipping creation"
    else
        run_command "docker network create spiritual-chatbot-traefik-public" "Creating Docker network"
    fi
    
    # Step 2: Build Docker images
    print_status "STEP 2/5: Building Docker images..."
    run_command "docker-compose build prestart frontend" "Building prestart and frontend images"
    
    # Step 3: Start services
    print_status "STEP 3/5: Starting services..."
    run_command "docker-compose up -d" "Starting all services"
    
    # Show container status
    print_status "Container status after startup:"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    
    # Wait for backend to be ready
    if ! wait_for_backend; then
        print_error "Backend container failed to start properly"
        print_status "You can try to continue manually or restart the script"
        print_status "Manual commands:"
        print_status "1. Check logs: docker-compose logs backend"
        print_status "2. Restart backend: docker-compose restart backend"
        print_status "3. Reset everything: docker-compose down && docker-compose up -d"
        
        # Ask user if they want to continue anyway
        echo ""
        read -p "Do you want to continue with user creation anyway? (y/N): " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_status "Setup stopped. You can run the script again or check the logs."
            exit 1
        fi
    fi
    
    # Step 4: Reset users
    print_status "STEP 4/5: Resetting users..."
    if ! execute_backend_command "python /app/scripts/docker_reset_users.py" "Resetting users"; then
        print_warning "User reset failed, but continuing..."
    fi
    
    # Step 5: Add test AI souls
    print_status "STEP 5/5: Adding test AI souls..."
    if ! execute_backend_command "python /app/scripts/add_test_ai_souls.py admin@example.com" "Adding test AI souls"; then
        print_warning "AI souls creation failed, but setup is mostly complete"
    fi
    
    # Clean up temp files
    rm -f /tmp/backend_container_name
    
    echo ""
    echo "=========================================="
    print_success "Setup completed!"
    echo "=========================================="
    echo ""
    print_status "Your AI Persona application should now be running!"
    echo -e "${GREEN}Access the application at: http://localhost:19100${NC}"
    echo ""
    print_status "Default login credentials:"
    echo "  Email: admin@example.com"
    echo "  Password: TestPass123!"
    echo ""
    print_status "Useful commands:"
    print_status "  View logs: docker-compose logs -f"
    print_status "  Stop services: docker-compose down"
    print_status "  Restart services: docker-compose restart"
    print_status "  Check status: docker ps"
    echo ""
    print_status "If you encounter issues, check the logs or restart specific services."
}

# Function to handle script interruption
cleanup() {
    print_warning "Script interrupted. Cleaning up..."
    rm -f /tmp/backend_container_name
    exit 1
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Check if script is being run from the project root
if [ ! -f "docker-compose.yml" ]; then
    print_error "This script must be run from the project root directory (where docker-compose.yml is located)"
    exit 1
fi

# Run main function
main "$@" 