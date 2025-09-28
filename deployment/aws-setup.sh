#!/bin/bash

# AWS EC2 Setup Script for Brahma Vastu Backend
# This script sets up an Ubuntu EC2 instance for FastAPI deployment

set -e

echo "🚀 Starting AWS EC2 setup for Brahma Vastu Backend..."

# Update system packages
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python 3.11 and pip
echo "🐍 Installing Python 3.11..."
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip

# Install system dependencies
echo "📚 Installing system dependencies..."
sudo apt install -y \
    nginx \
    mysql-server \
    git \
    curl \
    wget \
    unzip \
    build-essential \
    libssl-dev \
    libffi-dev \
    libmysqlclient-dev \
    pkg-config

# Install Node.js (for potential frontend builds)
echo "📦 Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Create application user
echo "👤 Creating application user..."
sudo useradd -m -s /bin/bash bvapp || echo "User bvapp already exists"
sudo usermod -aG sudo bvapp

# Create application directory
echo "📁 Setting up application directory..."
sudo mkdir -p /var/www/bv-backend
sudo chown -R bvapp:bvapp /var/www/bv-backend

# Setup MySQL
echo "🗄️ Configuring MySQL..."
sudo mysql_secure_installation <<EOF
n
y
your_mysql_root_password
your_mysql_root_password
y
y
y
y
EOF

# Create database and user
sudo mysql -u root -p <<EOF
CREATE DATABASE IF NOT EXISTS brahmavastu;
CREATE USER IF NOT EXISTS 'bvuser'@'localhost' IDENTIFIED BY 'bv_password_2024';
GRANT ALL PRIVILEGES ON brahmavastu.* TO 'bvuser'@'localhost';
FLUSH PRIVILEGES;
EOF

# Install Python dependencies
echo "🐍 Setting up Python virtual environment..."
cd /var/www/bv-backend
sudo -u bvapp python3.11 -m venv venv
sudo -u bvapp ./venv/bin/pip install --upgrade pip
sudo -u bvapp ./venv/bin/pip install -r requirements.txt

# Setup nginx
echo "🌐 Configuring nginx..."
sudo cp nginx.conf /etc/nginx/sites-available/bv-backend
sudo ln -sf /etc/nginx/sites-available/bv-backend /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx

# Setup systemd service
echo "⚙️ Creating systemd service..."
sudo tee /etc/systemd/system/bv-backend.service > /dev/null <<EOF
[Unit]
Description=Brahma Vastu Backend API
After=network.target mysql.service

[Service]
Type=exec
User=bvapp
Group=bvapp
WorkingDirectory=/var/www/bv-backend
Environment=PATH=/var/www/bv-backend/venv/bin
ExecStart=/var/www/bv-backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
ExecReload=/bin/kill -HUP \$MAINPID
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Enable and start services
echo "🔄 Starting services..."
sudo systemctl daemon-reload
sudo systemctl enable bv-backend
sudo systemctl start bv-backend
sudo systemctl enable mysql
sudo systemctl start mysql

# Setup log rotation
echo "📝 Setting up log rotation..."
sudo tee /etc/logrotate.d/bv-backend > /dev/null <<EOF
/var/www/bv-backend/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 bvapp bvapp
    postrotate
        systemctl reload bv-backend
    endscript
}
EOF

# Setup firewall
echo "🔥 Configuring firewall..."
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

# Create deployment script
echo "📜 Creating deployment script..."
sudo tee /var/www/bv-backend/deploy.sh > /dev/null <<EOF
#!/bin/bash
set -e

echo "🚀 Deploying Brahma Vastu Backend..."

# Pull latest changes
git pull origin main

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Restart services
sudo systemctl restart bv-backend
sudo systemctl reload nginx

echo "✅ Deployment completed successfully!"
EOF

sudo chmod +x /var/www/bv-backend/deploy.sh
sudo chown bvapp:bvapp /var/www/bv-backend/deploy.sh

echo "✅ AWS EC2 setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Upload your application code to /var/www/bv-backend"
echo "2. Configure your environment variables in .env file"
echo "3. Run database migrations: sudo -u bvapp /var/www/bv-backend/venv/bin/alembic upgrade head"
echo "4. Test the application: curl http://localhost/health"
echo ""
echo "🔧 Useful commands:"
echo "- Check service status: sudo systemctl status bv-backend"
echo "- View logs: sudo journalctl -u bv-backend -f"
echo "- Deploy updates: /var/www/bv-backend/deploy.sh"
