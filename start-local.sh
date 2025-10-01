#!/bin/bash

# Brahma Vastu Backend - Local Development Startup Script
# This script starts the complete local development environment

echo "🚀 Starting Brahma Vastu Backend - Local Development Environment"
echo "=================================================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker first."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Error: docker-compose is not installed. Please install docker-compose first."
    exit 1
fi

echo "✅ Docker is running"
echo "✅ docker-compose is available"

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p uploads logs app/static

# Start services
echo "🐳 Starting Docker services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."

# Wait for MySQL to be ready
echo "🔍 Checking MySQL connection..."
for i in {1..30}; do
    if docker exec bv-mysql mysqladmin ping -h localhost -u root -proot > /dev/null 2>&1; then
        echo "✅ MySQL is ready"
        break
    fi
    echo "⏳ Waiting for MySQL... ($i/30)"
    sleep 2
done

# Wait for FastAPI to be ready
echo "🔍 Checking FastAPI connection..."
for i in {1..30}; do
    if curl -f http://localhost/health > /dev/null 2>&1; then
        echo "✅ FastAPI is ready"
        break
    fi
    echo "⏳ Waiting for FastAPI... ($i/30)"
    sleep 2
done

# Check service status
echo "📊 Service Status:"
echo "=================="
docker-compose ps

echo ""
echo "🎉 Local Development Environment Started Successfully!"
echo "====================================================="
echo ""
echo "📋 Available Services:"
echo "  • API Backend:    http://localhost"
echo "  • API Docs:       http://localhost/docs"
echo "  • Health Check:   http://localhost/health"
echo "  • MySQL:          localhost:3306"
echo ""
echo "🔧 Database Information:"
echo "  • Database:       brahmavastu"
echo "  • User:           bvuser"
echo "  • Password:       bv_password"
echo "  • Root Password:  root"
echo ""
echo "📝 Useful Commands:"
echo "  • View logs:     docker-compose logs -f"
echo "  • Stop services: docker-compose down"
echo "  • Restart:       docker-compose restart"
echo "  • Database CLI:   docker exec -it bv-mysql mysql -u bvuser -p brahmavastu"
echo ""
echo "🚀 You can now start developing!"
