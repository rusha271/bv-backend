# AWS Deployment Files

This directory contains all the necessary files for deploying the Brahma Vastu Backend application on AWS.

## Files Overview

### Core Infrastructure
- **`aws-cloudformation.yaml`** - CloudFormation template defining all AWS resources
- **`aws-deploy.sh`** - Linux/Mac deployment script
- **`aws-deploy.ps1`** - Windows PowerShell deployment script
- **`aws-parameters.json`** - CloudFormation parameters
- **`aws-config.yaml`** - Deployment configuration

### Environment Configuration
- **`env.aws.production`** - Production environment variables for AWS
- **`cloudwatch-config.json`** - CloudWatch agent configuration
- **`alarms.json`** - CloudWatch alarms configuration

### Monitoring and Logging
- **`setup-monitoring.sh`** - Script to setup monitoring and alerting
- **`dashboard.json`** - CloudWatch dashboard configuration

### Documentation
- **`README.md`** - This file
- **`../AWS_DEPLOYMENT_GUIDE.md`** - Comprehensive deployment guide

## Quick Start

### Prerequisites
1. AWS CLI configured with appropriate permissions
2. EC2 Key Pair created
3. Python 3.11+ installed
4. Git installed

### Deploy Infrastructure

#### Linux/Mac
```bash
# Make script executable
chmod +x deployment/aws-deploy.sh

# Deploy everything
./deployment/aws-deploy.sh deploy
```

#### Windows
```powershell
# Run PowerShell script
.\deployment\aws-deploy.ps1 -Action deploy
```

### Setup Monitoring
```bash
# Setup monitoring and alerting
./deployment/setup-monitoring.sh setup
```

## Configuration

### Parameters
Edit `aws-parameters.json` to customize:
- Instance types
- Database configuration
- Environment settings
- Security settings

### Environment Variables
Edit `env.aws.production` to set:
- Database connection
- JWT secrets
- CORS origins
- AWS settings

## Architecture

The deployment creates:
- **VPC** with public/private subnets
- **Application Load Balancer** for traffic distribution
- **Auto Scaling Group** for automatic scaling
- **RDS MySQL** for database
- **S3 Bucket** for file storage
- **CloudWatch** for monitoring
- **Security Groups** for network security

## Monitoring

### CloudWatch Dashboard
- Application metrics
- System metrics
- Database metrics
- Load balancer metrics

### Alarms
- CPU utilization
- Memory usage
- Disk space
- Application errors
- Response time
- Database connections

### Logs
- Application logs
- Nginx logs
- System logs
- Database logs

## Security

### Network Security
- VPC with isolated subnets
- Security groups with minimal access
- Load balancer in public subnet
- Database in private subnet

### Data Security
- RDS encryption at rest
- S3 encryption enabled
- SSL/TLS for communications
- Regular security updates

### Access Control
- IAM roles with minimal permissions
- No hardcoded credentials
- Secure parameter storage

## Cost Optimization

### Instance Types
- **Development**: t3.small
- **Production**: t3.medium
- **High Load**: t3.large

### Database
- **Development**: db.t3.micro
- **Production**: db.t3.small

### Storage
- **EBS**: GP2 storage
- **S3**: Standard storage class
- **Backups**: 7-day retention

## Troubleshooting

### Common Issues
1. **Stack creation fails**: Check CloudFormation events
2. **Application not starting**: Check instance logs
3. **Database connection issues**: Check security groups
4. **Load balancer health checks failing**: Check application logs

### Debug Commands
```bash
# Check stack status
aws cloudformation describe-stacks --stack-name bv-backend-infrastructure

# Check instance status
aws ec2 describe-instances --filters "Name=tag:Name,Values=bv-backend-infrastructure-WebServer"

# Check load balancer
aws elbv2 describe-load-balancers --names bv-backend-infrastructure-ALB

# Check RDS status
aws rds describe-db-instances --db-instance-identifier bv-backend-infrastructure-database
```

## Maintenance

### Regular Tasks
- Security updates
- Database backups
- Log rotation
- Cost review
- Performance monitoring

### Scaling
- Horizontal: Auto Scaling Group
- Vertical: Change instance types
- Database: RDS scaling
- Storage: S3 lifecycle policies

## Support

For issues and questions:
1. Check CloudWatch logs
2. Review CloudFormation events
3. Check AWS documentation
4. Contact AWS support

## Additional Resources

- [AWS CloudFormation Documentation](https://docs.aws.amazon.com/cloudformation/)
- [AWS RDS Documentation](https://docs.aws.amazon.com/rds/)
- [AWS Application Load Balancer Documentation](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/)
- [AWS CloudWatch Documentation](https://docs.aws.amazon.com/cloudwatch/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [MySQL Documentation](https://dev.mysql.com/doc/)
