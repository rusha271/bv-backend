# Brahma Vastu Backend Deployment Guide

This guide covers multiple deployment options for the Brahma Vastu Backend API.

## Table of Contents

1. [Local Development Setup](#local-development-setup)
2. [AWS EC2 Deployment](#aws-ec2-deployment)
3. [Docker Deployment](#docker-deployment)
4. [AWS CloudFormation Deployment](#aws-cloudformation-deployment)
5. [Environment Configuration](#environment-configuration)
6. [Database Setup](#database-setup)
7. [Monitoring and Maintenance](#monitoring-and-maintenance)

## Local Development Setup

### Prerequisites

- Python 3.11+
- MySQL 8.0+
- Git

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd bv-backend
   ```

2. **Create virtual environment**
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup environment variables**
   ```bash
   cp env.development.example .env
   # Edit .env with your configuration
   ```

5. **Setup MySQL database**
   ```bash
   mysql -u root -p
   CREATE DATABASE brahmavastu;
   CREATE USER 'bvuser'@'localhost' IDENTIFIED BY 'bv_password';
   GRANT ALL PRIVILEGES ON brahmavastu.* TO 'bvuser'@'localhost';
   FLUSH PRIVILEGES;
   ```

6. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

7. **Start the application**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

## AWS EC2 Deployment

### Prerequisites

- AWS Account
- EC2 Key Pair
- Domain name (optional)

### Setup Steps

1. **Launch EC2 Instance**
   - Choose Ubuntu 22.04 LTS
   - Instance type: t3.medium or larger
   - Security groups: SSH (22), HTTP (80), HTTPS (443)

2. **Connect to EC2 Instance**
   ```bash
   ssh -i your-key.pem ubuntu@your-ec2-ip
   ```

3. **Run the setup script**
   ```bash
   # Upload the setup script to your EC2 instance
   chmod +x aws-setup.sh
   sudo ./aws-setup.sh
   ```

4. **Upload your application code**
   ```bash
   # Clone your repository
   cd /var/www/bv-backend
   git clone <your-repository-url> .
   
   # Set proper permissions
   sudo chown -R bvapp:bvapp /var/www/bv-backend
   ```

5. **Configure environment**
   ```bash
   cp env.production.example .env
   # Edit .env with your production values
   ```

6. **Run database migrations**
   ```bash
   sudo -u bvapp /var/www/bv-backend/venv/bin/alembic upgrade head
   ```

7. **Start the application**
   ```bash
   sudo systemctl start bv-backend
   sudo systemctl enable bv-backend
   ```

## Docker Deployment

### Prerequisites

- Docker
- Docker Compose

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd bv-backend
   ```

2. **Configure environment**
   ```bash
   cp env.production.example .env
   # Edit .env with your configuration
   ```

3. **Start the services**
   ```bash
   docker-compose up -d
   ```

4. **Run database migrations**
   ```bash
   docker-compose exec app alembic upgrade head
   ```

5. **Check service status**
   ```bash
   docker-compose ps
   docker-compose logs -f
   ```

## AWS CloudFormation Deployment

### Prerequisites

- AWS CLI configured
- AWS CloudFormation access

### Setup Steps

1. **Prepare the template**
   ```bash
   # Update the CloudFormation template with your parameters
   # Edit deployment/aws-cloudformation.yaml
   ```

2. **Deploy the stack**
   ```bash
   aws cloudformation create-stack \
     --stack-name bv-backend-stack \
     --template-body file://deployment/aws-cloudformation.yaml \
     --parameters ParameterKey=KeyPairName,ParameterValue=your-keypair \
     --capabilities CAPABILITY_IAM
   ```

3. **Wait for stack creation**
   ```bash
   aws cloudformation wait stack-create-complete \
     --stack-name bv-backend-stack
   ```

4. **Get stack outputs**
   ```bash
   aws cloudformation describe-stacks \
     --stack-name bv-backend-stack \
     --query 'Stacks[0].Outputs'
   ```

## Environment Configuration

### Development Environment

Use `env.development.example` as a template:

```bash
cp env.development.example .env
```

Key settings:
- `ENVIRONMENT=development`
- `DATABASE_URL=mysql+pymysql://root:root@localhost/brahmavastu`
- `LOG_LEVEL=DEBUG`

### Production Environment

Use `env.production.example` as a template:

```bash
cp env.production.example .env
```

Key settings:
- `ENVIRONMENT=production`
- `DATABASE_URL=mysql+pymysql://bvuser:secure_password@localhost/brahmavastu`
- `LOG_LEVEL=INFO`
- Secure JWT and encryption keys

### AWS Environment

Use `env.aws.example` as a template:

```bash
cp env.aws.example .env
```

Key settings:
- `ENVIRONMENT=aws_rds`
- `DATABASE_URL=mysql+pymysql://admin:password@rds-endpoint:3306/brahmavastu`
- AWS-specific configurations

## Database Setup

### Local MySQL Setup

1. **Install MySQL**
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install mysql-server
   
   # macOS
   brew install mysql
   ```

2. **Secure MySQL installation**
   ```bash
   sudo mysql_secure_installation
   ```

3. **Create database and user**
   ```sql
   CREATE DATABASE brahmavastu;
   CREATE USER 'bvuser'@'localhost' IDENTIFIED BY 'secure_password';
   GRANT ALL PRIVILEGES ON brahmavastu.* TO 'bvuser'@'localhost';
   FLUSH PRIVILEGES;
   ```

### AWS RDS Setup

1. **Create RDS instance**
   - Engine: MySQL 8.0
   - Instance class: db.t3.micro (for testing)
   - Storage: 20 GB
   - Enable encryption

2. **Configure security groups**
   - Allow MySQL (3306) from your EC2 security group

3. **Update environment variables**
   ```bash
   DATABASE_URL=mysql+pymysql://admin:password@your-rds-endpoint:3306/brahmavastu
   ```

## Monitoring and Maintenance

### Health Checks

```bash
# Check application health
curl http://localhost:8000/health

# Check service status
sudo systemctl status bv-backend

# Check nginx status
sudo systemctl status nginx
```

### Logs

```bash
# Application logs
sudo journalctl -u bv-backend -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Database Maintenance

```bash
# Backup database
mysqldump -u root -p brahmavastu > backup.sql

# Restore database
mysql -u root -p brahmavastu < backup.sql
```

### Updates and Deployments

```bash
# Use the deployment script
./deployment/deploy.sh deploy

# Or manually
git pull origin main
sudo systemctl restart bv-backend
```

## Security Considerations

1. **Environment Variables**
   - Never commit `.env` files
   - Use strong, unique passwords
   - Rotate secrets regularly

2. **Database Security**
   - Use strong passwords
   - Enable SSL connections
   - Regular backups

3. **Server Security**
   - Keep system updated
   - Use firewall rules
   - Monitor logs

4. **Application Security**
   - Rate limiting enabled
   - CORS properly configured
   - Input validation

## Troubleshooting

### Common Issues

1. **Database Connection Issues**
   - Check database credentials
   - Verify database is running
   - Check network connectivity

2. **Service Won't Start**
   - Check logs: `sudo journalctl -u bv-backend -f`
   - Verify environment variables
   - Check file permissions

3. **Nginx Issues**
   - Test configuration: `sudo nginx -t`
   - Check error logs: `sudo tail -f /var/log/nginx/error.log`

4. **Permission Issues**
   - Ensure proper ownership: `sudo chown -R bvapp:bvapp /var/www/bv-backend`
   - Check file permissions: `ls -la /var/www/bv-backend`

### Getting Help

- Check application logs
- Review nginx error logs
- Verify database connectivity
- Test individual components

## Support

For deployment issues or questions, please refer to the application logs and this guide. The deployment scripts include comprehensive error handling and logging to help diagnose issues.
