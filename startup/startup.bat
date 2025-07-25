@echo off
:: AI Persona Project Startup Script for Windows
:: This script automates the complete setup process for the AI Persona project

setlocal enabledelayedexpansion

:: Color codes for Windows (limited support)
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "NC=[0m"

:: Function to print colored output (simulated with goto)
:print_status
echo %BLUE%[INFO]%NC% %~1
goto :eof

:print_success
echo %GREEN%[SUCCESS]%NC% %~1
goto :eof

:print_warning
echo %YELLOW%[WARNING]%NC% %~1
goto :eof

:print_error
echo %RED%[ERROR]%NC% %~1
goto :eof

:run_command
echo.
call :print_status "Running: %~2"
echo Command: %~1
echo ----------------------------------------
%~1
if %errorlevel% neq 0 (
    call :print_error "%~2 failed"
    echo.
    exit /b 1
) else (
    call :print_success "%~2 completed successfully"
    echo.
)
goto :eof

:check_docker
call :print_status "Checking Docker installation and status..."

where docker >nul 2>nul
if %errorlevel% neq 0 (
    call :print_error "Docker is not installed or not in PATH"
    echo Please install Docker and try again.
    exit /b 1
)

docker info >nul 2>nul
if %errorlevel% neq 0 (
    call :print_error "Docker is not running"
    echo Please start Docker Desktop and try again.
    exit /b 1
)

where docker-compose >nul 2>nul
if %errorlevel% neq 0 (
    call :print_error "Docker Compose is not installed or not in PATH"
    echo Please install Docker Compose and try again.
    exit /b 1
)

call :print_success "Docker and Docker Compose are ready"
goto :eof

:get_backend_container_name
:: Try to find the backend container dynamically
set backend_container=

:: Get all running container names and check for backend
for /f "tokens=*" %%i in ('docker ps --filter "status=running" --format "{{.Names}}" 2^>nul') do (
    set container_name=%%i
    echo !container_name! | findstr /i "backend" >nul
    if !errorlevel! equ 0 (
        set backend_container=!container_name!
        goto :eof
    )
)

goto :eof

:wait_for_backend
call :print_status "Waiting for backend container to be ready..."
set /a max_attempts=60
set /a attempt=0
set backend_container=

:container_search_loop
call :get_backend_container_name
if not "!backend_container!"=="" (
    call :print_success "Found backend container: !backend_container!"
    goto :health_check
)

echo|set /p="."
timeout /t 2 /nobreak >nul
set /a attempt+=1
if %attempt% lss %max_attempts% goto container_search_loop

call :print_error "Backend container not found after %max_attempts% attempts"
call :print_status "Available containers:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

:: Try fallback
call :print_status "Trying fallback container detection..."
for /f "tokens=*" %%i in ('docker ps --format "{{.Names}}" 2^>nul') do (
    echo %%i | findstr /i "backend" >nul
    if !errorlevel! equ 0 (
        set backend_container=%%i
        call :print_warning "Using fallback container: !backend_container!"
        goto :health_check
    )
)
exit /b 1

:health_check
set /a attempt=0
call :print_status "Waiting for backend health check..."

:health_loop
:: Check if container is running
docker ps --filter "name=!backend_container!" --filter "status=running" | findstr "!backend_container!" >nul 2>nul
if %errorlevel% neq 0 (
    call :print_error "Backend container !backend_container! is not running"
    docker ps --filter "name=!backend_container!" --format "table {{.Names}}\t{{.Status}}"
    exit /b 1
)

:: Check if API is responding
docker exec !backend_container! curl -f http://localhost:8000/api/utils/health-check/ >nul 2>nul
if %errorlevel% equ 0 (
    call :print_success "Backend container is healthy and ready"
    echo !backend_container! > backend_container_name.tmp
    goto :eof
)

:: Show progress every 10 attempts
set /a remainder=%attempt% %% 10
if %remainder% equ 0 (
    call :print_status "Still waiting for backend... (attempt %attempt%/%max_attempts%)"
    call :print_status "Recent backend logs:"
    docker logs !backend_container! --tail=5 2>nul
)

echo|set /p="."
timeout /t 2 /nobreak >nul
set /a attempt+=1
if %attempt% lss %max_attempts% goto health_loop

call :print_error "Backend container did not become healthy within expected time"
call :print_status "Final container status:"
docker ps --filter "name=!backend_container!" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

call :print_status "Backend container logs (last 20 lines):"
docker logs !backend_container! --tail=20 2>nul

exit /b 1

:execute_backend_command
set command=%~1
set description=%~2

:: Get backend container name
if exist backend_container_name.tmp (
    set /p backend_container=<backend_container_name.tmp
) else (
    call :get_backend_container_name
)

if "!backend_container!"=="" (
    call :print_error "Cannot find backend container"
    exit /b 1
)

call :print_status "Using backend container: !backend_container!"
call :run_command "docker exec -it !backend_container! %command%" "%description%"
goto :eof

:main
echo ==========================================
echo    AI Persona Project Startup Script     
echo ==========================================
echo.

call :print_status "Windows detected. Make sure Docker Desktop is running."
call :print_warning "If you encounter issues, try running this from Command Prompt as Administrator."
echo.

set /p continue="Do you want to continue with the setup? (y/N): "
if /i not "%continue%"=="y" (
    call :print_status "Setup cancelled by user"
    exit /b 0
)

call :check_docker
if %errorlevel% neq 0 exit /b 1

echo.
call :print_status "Starting AI Persona project setup..."
echo This will run the following commands in sequence:
echo 1. Create Docker network
echo 2. Build Docker images
echo 3. Start services
echo 4. Reset users
echo 5. Add test AI souls
echo.

:: Step 1: Create Docker network
call :print_status "STEP 1/5: Creating Docker network..."
docker network ls | findstr "spiritual-chatbot-traefik-public" >nul 2>nul
if %errorlevel% equ 0 (
    call :print_warning "Network 'spiritual-chatbot-traefik-public' already exists, skipping creation"
) else (
    call :run_command "docker network create spiritual-chatbot-traefik-public" "Creating Docker network"
    if %errorlevel% neq 0 exit /b 1
)

:: Step 2: Build Docker images
call :print_status "STEP 2/5: Building Docker images..."
call :run_command "docker-compose build prestart frontend" "Building prestart and frontend images"
if %errorlevel% neq 0 exit /b 1

:: Step 3: Start services
call :print_status "STEP 3/5: Starting services..."
call :run_command "docker-compose up -d" "Starting all services"
if %errorlevel% neq 0 exit /b 1

:: Show container status
call :print_status "Container status after startup:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

:: Wait for backend to be ready
call :wait_for_backend
if %errorlevel% neq 0 (
    call :print_error "Backend container failed to start properly"
    call :print_status "You can try to continue manually or restart the script"
    call :print_status "Manual commands:"
    call :print_status "1. Check logs: docker-compose logs backend"
    call :print_status "2. Restart backend: docker-compose restart backend"
    call :print_status "3. Reset everything: docker-compose down && docker-compose up -d"
    echo.
    set /p continue_anyway="Do you want to continue with user creation anyway? (y/N): "
    if /i not "!continue_anyway!"=="y" (
        call :print_status "Setup stopped. You can run the script again or check the logs."
        exit /b 1
    )
)

:: Step 4: Reset users
call :print_status "STEP 4/5: Resetting users..."
call :execute_backend_command "python /app/scripts/docker_reset_users.py" "Resetting users"
if %errorlevel% neq 0 (
    call :print_warning "User reset failed, but continuing..."
)

:: Step 5: Add test AI souls
call :print_status "STEP 5/5: Adding test AI souls..."
call :execute_backend_command "python /app/scripts/add_test_ai_souls.py admin@example.com" "Adding test AI souls"
if %errorlevel% neq 0 (
    call :print_warning "AI souls creation failed, but setup is mostly complete"
)

:: Clean up temp files
if exist backend_container_name.tmp del backend_container_name.tmp

echo.
echo ==========================================
call :print_success "Setup completed!"
echo ==========================================
echo.
call :print_status "Your AI Persona application should now be running!"
echo %GREEN%Access the application at: http://localhost:19100%NC%
echo.
call :print_status "Default login credentials:"
echo   Email: admin@example.com
echo   Password: TestPass123!
echo.
call :print_status "Useful commands:"
echo   View logs: docker-compose logs -f
echo   Stop services: docker-compose down
echo   Restart services: docker-compose restart
echo   Check status: docker ps
echo.
call :print_status "If you encounter issues, check the logs or restart specific services."
echo.
pause

goto :eof

:: Check if script is being run from the project root
if not exist "docker-compose.yml" (
    call :print_error "This script must be run from the project root directory (where docker-compose.yml is located)"
    pause
    exit /b 1
)

:: Run main function
call :main %* 