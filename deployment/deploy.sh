#!/bin/bash

# Brahma Vastu Backend Deployment Script
# This script handles deployment to different environments

set -e

# Configuration
APP_NAME="bv-backend"
APP_DIR="/var/www/bv-backend"
SERVICE_NAME="bv-backend"
NGINX_SITE="bv-backend"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_error "This script should not be run as root"
        exit 1
    fi
}

# Check if application directory exists
check_app_directory() {
    if [ ! -d "$APP_DIR" ]; then
        log_error "Application directory $APP_DIR does not exist"
        exit 1
    fi
}

# Backup current deployment
backup_deployment() {
    log_info "Creating backup of current deployment..."
    
    BACKUP_DIR="/var/backups/bv-backend/$(date +%Y%m%d_%H%M%S)"
    sudo mkdir -p "$BACKUP_DIR"
    
    # Backup application files
    sudo cp -r "$APP_DIR" "$BACKUP_DIR/"
    
    # Backup database (if MySQL is available)
    if command -v mysqldump &> /dev/null; then
        log_info "Backing up database..."
        sudo mysqldump -u root -p brahmavastu > "$BACKUP_DIR/database_backup.sql" 2>/dev/null || log_warning "Database backup failed"
    fi
    
    log_success "Backup created at $BACKUP_DIR"
}

# Update application code
update_code() {
    log_info "Updating application code..."
    
    cd "$APP_DIR"
    
    # Pull latest changes from git
    if [ -d ".git" ]; then
        git pull origin main || log_warning "Git pull failed, continuing with current code"
    else
        log_warning "Not a git repository, skipping git pull"
    fi
    
    log_success "Code updated successfully"
}

# Install/update dependencies
update_dependencies() {
    log_info "Updating Python dependencies..."
    
    cd "$APP_DIR"
    
    # Activate virtual environment
    if [ ! -d "venv" ]; then
        log_error "Virtual environment not found at $APP_DIR/venv"
        exit 1
    fi
    
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install/update requirements
    pip install -r requirements.txt
    
    log_success "Dependencies updated successfully"
}

# Run database migrations
run_migrations() {
    log_info "Running database migrations..."
    
    cd "$APP_DIR"
    source venv/bin/activate
    
    # Check if alembic is available
    if ! command -v alembic &> /dev/null; then
        log_error "Alembic not found. Please install it first."
        exit 1
    fi
    
    # Run migrations
    alembic upgrade head
    
    log_success "Database migrations completed"
}

# Update environment configuration
update_environment() {
    log_info "Updating environment configuration..."
    
    # Copy environment file if it exists
    if [ -f "env.production.example" ]; then
        if [ ! -f ".env" ]; then
            cp env.production.example .env
            log_warning "Created .env file from example. Please update with your actual values."
        fi
    fi
    
    log_success "Environment configuration updated"
}

# Restart services
restart_services() {
    log_info "Restarting services..."
    
    # Restart application service
    sudo systemctl restart "$SERVICE_NAME"
    
    # Check service status
    if sudo systemctl is-active --quiet "$SERVICE_NAME"; then
        log_success "Application service restarted successfully"
    else
        log_error "Failed to restart application service"
        sudo systemctl status "$SERVICE_NAME"
        exit 1
    fi
    
    # Reload nginx
    sudo nginx -t && sudo systemctl reload nginx
    log_success "Nginx configuration reloaded"
}

# Run health checks
health_check() {
    log_info "Running health checks..."
    
    # Wait for service to start
    sleep 5
    
    # Check if service is running
    if ! sudo systemctl is-active --quiet "$SERVICE_NAME"; then
        log_error "Service is not running"
        sudo systemctl status "$SERVICE_NAME"
        exit 1
    fi
    
    # Check if nginx is running
    if ! sudo systemctl is-active --quiet nginx; then
        log_error "Nginx is not running"
        sudo systemctl status nginx
        exit 1
    fi
    
    # Test health endpoint
    if curl -f http://localhost/health > /dev/null 2>&1; then
        log_success "Health check passed"
    else
        log_error "Health check failed"
        exit 1
    fi
}

# Cleanup old files
cleanup() {
    log_info "Cleaning up old files..."
    
    # Clean up old log files (keep last 7 days)
    find /var/log -name "*.log" -mtime +7 -delete 2>/dev/null || true
    
    # Clean up old backups (keep last 30 days)
    find /var/backups/bv-backend -type d -mtime +30 -exec rm -rf {} + 2>/dev/null || true
    
    log_success "Cleanup completed"
}

# Main deployment function
deploy() {
    log_info "Starting deployment of $APP_NAME..."
    
    # Pre-deployment checks
    check_root
    check_app_directory
    
    # Deployment steps
    backup_deployment
    update_code
    update_dependencies
    update_environment
    run_migrations
    restart_services
    health_check
    cleanup
    
    log_success "Deployment completed successfully!"
    log_info "Application is running at http://localhost"
    log_info "API documentation available at http://localhost/docs"
}

# Rollback function
rollback() {
    log_info "Rolling back deployment..."
    
    # Find latest backup
    LATEST_BACKUP=$(ls -t /var/backups/bv-backend/ | head -n1)
    
    if [ -z "$LATEST_BACKUP" ]; then
        log_error "No backup found for rollback"
        exit 1
    fi
    
    log_info "Rolling back to backup: $LATEST_BACKUP"
    
    # Stop service
    sudo systemctl stop "$SERVICE_NAME"
    
    # Restore from backup
    sudo rm -rf "$APP_DIR"
    sudo cp -r "/var/backups/bv-backend/$LATEST_BACKUP/$APP_NAME" "$APP_DIR"
    sudo chown -R bvapp:bvapp "$APP_DIR"
    
    # Restart service
    sudo systemctl start "$SERVICE_NAME"
    
    log_success "Rollback completed"
}

# Show usage
usage() {
    echo "Usage: $0 [deploy|rollback|status|logs]"
    echo ""
    echo "Commands:"
    echo "  deploy   - Deploy the application"
    echo "  rollback - Rollback to previous version"
    echo "  status   - Show service status"
    echo "  logs     - Show application logs"
    exit 1
}

# Show status
show_status() {
    log_info "Service Status:"
    sudo systemctl status "$SERVICE_NAME" --no-pager
    echo ""
    log_info "Nginx Status:"
    sudo systemctl status nginx --no-pager
}

# Show logs
show_logs() {
    log_info "Application Logs:"
    sudo journalctl -u "$SERVICE_NAME" -f --no-pager
}

# Main script logic
case "${1:-deploy}" in
    deploy)
        deploy
        ;;
    rollback)
        rollback
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    *)
        usage
        ;;
esac
