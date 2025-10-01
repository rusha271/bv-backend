@echo off
REM Brahma Vastu Backend - Local Development Startup Script
REM This script starts the complete local development environment

echo 🚀 Starting Brahma Vastu Backend - Local Development Environment
echo ==================================================================

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Error: Docker is not running. Please start Docker first.
    pause
    exit /b 1
)

REM Check if docker-compose is available
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Error: docker-compose is not installed. Please install docker-compose first.
    pause
    exit /b 1
)

echo ✅ Docker is running
echo ✅ docker-compose is available

REM Create necessary directories
echo 📁 Creating necessary directories...
if not exist "uploads" mkdir uploads
if not exist "logs" mkdir logs
if not exist "app\static" mkdir app\static

REM Start services
echo 🐳 Starting Docker services...
docker-compose up -d

REM Wait for services to be ready
echo ⏳ Waiting for services to be ready...

REM Wait for MySQL to be ready
echo 🔍 Checking MySQL connection...
for /L %%i in (1,1,30) do (
    docker exec bv-mysql mysqladmin ping -h localhost -u root -proot >nul 2>&1
    if !errorlevel! equ 0 (
        echo ✅ MySQL is ready
        goto :mysql_ready
    )
    echo ⏳ Waiting for MySQL... (%%i/30)
    timeout /t 2 /nobreak >nul
)
:mysql_ready

REM Wait for FastAPI to be ready
echo 🔍 Checking FastAPI connection...
for /L %%i in (1,1,30) do (
    curl -f http://localhost/health >nul 2>&1
    if !errorlevel! equ 0 (
        echo ✅ FastAPI is ready
        goto :fastapi_ready
    )
    echo ⏳ Waiting for FastAPI... (%%i/30)
    timeout /t 2 /nobreak >nul
)
:fastapi_ready

REM Check service status
echo 📊 Service Status:
echo ==================
docker-compose ps

echo.
echo 🎉 Local Development Environment Started Successfully!
echo =====================================================
echo.
echo 📋 Available Services:
echo   • API Backend:    http://localhost
echo   • API Docs:       http://localhost/docs
echo   • Health Check:   http://localhost/health
echo   • MySQL:          localhost:3306
echo.
echo 🔧 Database Information:
echo   • Database:       brahmavastu
echo   • User:           bvuser
echo   • Password:       bv_password
echo   • Root Password:  root
echo.
echo 📝 Useful Commands:
echo   • View logs:     docker-compose logs -f
echo   • Stop services: docker-compose down
echo   • Restart:       docker-compose restart
echo   • Database CLI:  docker exec -it bv-mysql mysql -u bvuser -p brahmavastu
echo.
echo 🚀 You can now start developing!
pause
