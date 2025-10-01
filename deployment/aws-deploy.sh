#!/bin/bash

# AWS Deployment Script for Brahma Vastu Backend
# This script automates the deployment of the infrastructure and application

set -e

# Configuration
STACK_NAME="bv-backend-infrastructure"
REGION="us-east-1"
TEMPLATE_FILE="deployment/aws-cloudformation.yaml"
PARAMETERS_FILE="deployment/aws-parameters.json"
KEY_PAIR_NAME="bv-backend-keypair"
INSTANCE_TYPE="t3.medium"
DB_INSTANCE_CLASS="db.t3.micro"
ENVIRONMENT="production"

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

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if AWS CLI is installed
    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI is not installed. Please install it first."
        exit 1
    fi
    
    # Check if AWS CLI is configured
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS CLI is not configured. Please run 'aws configure' first."
        exit 1
    fi
    
    # Check if jq is installed
    if ! command -v jq &> /dev/null; then
        log_error "jq is not installed. Please install it first."
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Create parameters file
create_parameters_file() {
    log_info "Creating parameters file..."
    
    cat > "$PARAMETERS_FILE" << EOF
[
    {
        "ParameterKey": "KeyPairName",
        "ParameterValue": "$KEY_PAIR_NAME"
    },
    {
        "ParameterKey": "InstanceType",
        "ParameterValue": "$INSTANCE_TYPE"
    },
    {
        "ParameterKey": "DBInstanceClass",
        "ParameterValue": "$DB_INSTANCE_CLASS"
    },
    {
        "ParameterKey": "DBUsername",
        "ParameterValue": "admin"
    },
    {
        "ParameterKey": "DBPassword",
        "ParameterValue": "$(openssl rand -base64 32)"
    },
    {
        "ParameterKey": "Environment",
        "ParameterValue": "$ENVIRONMENT"
    }
]
EOF
    
    log_success "Parameters file created: $PARAMETERS_FILE"
}

# Validate CloudFormation template
validate_template() {
    log_info "Validating CloudFormation template..."
    
    if aws cloudformation validate-template --template-body file://"$TEMPLATE_FILE" --region "$REGION" > /dev/null; then
        log_success "CloudFormation template is valid"
    else
        log_error "CloudFormation template validation failed"
        exit 1
    fi
}

# Deploy infrastructure
deploy_infrastructure() {
    log_info "Deploying infrastructure..."
    
    # Check if stack exists
    if aws cloudformation describe-stacks --stack-name "$STACK_NAME" --region "$REGION" &> /dev/null; then
        log_info "Stack exists, updating..."
        aws cloudformation update-stack \
            --stack-name "$STACK_NAME" \
            --template-body file://"$TEMPLATE_FILE" \
            --parameters file://"$PARAMETERS_FILE" \
            --capabilities CAPABILITY_IAM \
            --region "$REGION"
        
        log_info "Waiting for stack update to complete..."
        aws cloudformation wait stack-update-complete --stack-name "$STACK_NAME" --region "$REGION"
    else
        log_info "Creating new stack..."
        aws cloudformation create-stack \
            --stack-name "$STACK_NAME" \
            --template-body file://"$TEMPLATE_FILE" \
            --parameters file://"$PARAMETERS_FILE" \
            --capabilities CAPABILITY_IAM \
            --region "$REGION"
        
        log_info "Waiting for stack creation to complete..."
        aws cloudformation wait stack-create-complete --stack-name "$STACK_NAME" --region "$REGION"
    fi
    
    log_success "Infrastructure deployment completed"
}

# Get stack outputs
get_stack_outputs() {
    log_info "Getting stack outputs..."
    
    OUTPUTS=$(aws cloudformation describe-stacks --stack-name "$STACK_NAME" --region "$REGION" --query 'Stacks[0].Outputs' --output json)
    
    LOAD_BALANCER_DNS=$(echo "$OUTPUTS" | jq -r '.[] | select(.OutputKey=="LoadBalancerDNS") | .OutputValue')
    DATABASE_ENDPOINT=$(echo "$OUTPUTS" | jq -r '.[] | select(.OutputKey=="DatabaseEndpoint") | .OutputValue')
    S3_BUCKET_NAME=$(echo "$OUTPUTS" | jq -r '.[] | select(.OutputKey=="S3BucketName") | .OutputValue')
    
    log_success "Stack outputs retrieved"
    log_info "Load Balancer DNS: $LOAD_BALANCER_DNS"
    log_info "Database Endpoint: $DATABASE_ENDPOINT"
    log_info "S3 Bucket: $S3_BUCKET_NAME"
}

# Create deployment package
create_deployment_package() {
    log_info "Creating deployment package..."
    
    # Create deployment directory
    DEPLOY_DIR="deployment/package"
    mkdir -p "$DEPLOY_DIR"
    
    # Copy application files
    cp -r app "$DEPLOY_DIR/"
    cp -r alembic "$DEPLOY_DIR/"
    cp requirements.txt "$DEPLOY_DIR/"
    cp alembic.ini "$DEPLOY_DIR/"
    cp Dockerfile "$DEPLOY_DIR/"
    cp docker-compose.yml "$DEPLOY_DIR/"
    cp nginx.conf "$DEPLOY_DIR/"
    
    # Create deployment script
    cat > "$DEPLOY_DIR/deploy.sh" << 'EOF'
#!/bin/bash
set -e

echo "🚀 Deploying Brahma Vastu Backend..."

# Update system
sudo yum update -y

# Install Python 3.11
sudo yum install -y python3 python3-pip git nginx

# Create application user
sudo useradd -m -s /bin/bash bvapp || echo "User already exists"

# Create application directory
sudo mkdir -p /var/www/bv-backend
sudo chown -R bvapp:bvapp /var/www/bv-backend

# Copy application files
sudo cp -r /tmp/deployment/* /var/www/bv-backend/
sudo chown -R bvapp:bvapp /var/www/bv-backend

# Setup Python virtual environment
cd /var/www/bv-backend
sudo -u bvapp python3 -m venv venv
sudo -u bvapp ./venv/bin/pip install --upgrade pip
sudo -u bvapp ./venv/bin/pip install -r requirements.txt

# Setup nginx
sudo cp nginx.conf /etc/nginx/conf.d/bv-backend.conf
sudo systemctl enable nginx
sudo systemctl start nginx

# Create systemd service
sudo tee /etc/systemd/system/bv-backend.service > /dev/null << 'SERVICE_EOF'
[Unit]
Description=Brahma Vastu Backend API
After=network.target

[Service]
Type=exec
User=bvapp
Group=bvapp
WorkingDirectory=/var/www/bv-backend
Environment=PATH=/var/www/bv-backend/venv/bin
ExecStart=/var/www/bv-backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
SERVICE_EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable bv-backend
sudo systemctl start bv-backend

echo "✅ Deployment completed successfully!"
EOF
    
    chmod +x "$DEPLOY_DIR/deploy.sh"
    
    # Create zip package
    cd "$DEPLOY_DIR"
    zip -r "../bv-backend-deployment.zip" .
    cd ..
    
    log_success "Deployment package created: deployment/bv-backend-deployment.zip"
}

# Deploy application to instances
deploy_application() {
    log_info "Deploying application to instances..."
    
    # Get Auto Scaling Group name
    ASG_NAME=$(aws cloudformation describe-stacks --stack-name "$STACK_NAME" --region "$REGION" --query 'Stacks[0].Outputs[?OutputKey==`AutoScalingGroupName`].OutputValue' --output text)
    
    # Get instance IDs
    INSTANCE_IDS=$(aws autoscaling describe-auto-scaling-groups --auto-scaling-group-names "$ASG_NAME" --region "$REGION" --query 'AutoScalingGroups[0].Instances[].InstanceId' --output text)
    
    for INSTANCE_ID in $INSTANCE_IDS; do
        log_info "Deploying to instance: $INSTANCE_ID"
        
        # Copy deployment package to instance
        aws ssm send-command \
            --instance-ids "$INSTANCE_ID" \
            --document-name "AWS-RunShellScript" \
            --parameters 'commands=["sudo yum install -y unzip", "cd /tmp && unzip -o /tmp/bv-backend-deployment.zip", "sudo ./deploy.sh"]' \
            --region "$REGION" \
            --output text
    done
    
    log_success "Application deployment initiated"
}

# Setup monitoring
setup_monitoring() {
    log_info "Setting up monitoring..."
    
    # Create CloudWatch dashboard
    cat > deployment/dashboard.json << EOF
{
    "widgets": [
        {
            "type": "metric",
            "properties": {
                "metrics": [
                    ["AWS/ApplicationELB", "TargetResponseTime", "LoadBalancer", "$LOAD_BALANCER_DNS"],
                    ["AWS/ApplicationELB", "RequestCount", "LoadBalancer", "$LOAD_BALANCER_DNS"],
                    ["AWS/ApplicationELB", "HTTPCode_Target_2XX_Count", "LoadBalancer", "$LOAD_BALANCER_DNS"],
                    ["AWS/ApplicationELB", "HTTPCode_Target_4XX_Count", "LoadBalancer", "$LOAD_BALANCER_DNS"],
                    ["AWS/ApplicationELB", "HTTPCode_Target_5XX_Count", "LoadBalancer", "$LOAD_BALANCER_DNS"]
                ],
                "period": 300,
                "stat": "Average",
                "region": "$REGION",
                "title": "Application Load Balancer Metrics"
            }
        }
    ]
}
EOF
    
    # Create dashboard
    aws cloudwatch put-dashboard \
        --dashboard-name "BV-Backend-Dashboard" \
        --dashboard-body file://deployment/dashboard.json \
        --region "$REGION"
    
    log_success "Monitoring setup completed"
}

# Cleanup
cleanup() {
    log_info "Cleaning up temporary files..."
    rm -f "$PARAMETERS_FILE"
    rm -rf deployment/package
    rm -f deployment/bv-backend-deployment.zip
    rm -f deployment/dashboard.json
    log_success "Cleanup completed"
}

# Show deployment information
show_deployment_info() {
    log_success "Deployment completed successfully!"
    echo ""
    echo "📋 Deployment Information:"
    echo "Stack Name: $STACK_NAME"
    echo "Region: $REGION"
    echo "Load Balancer URL: http://$LOAD_BALANCER_DNS"
    echo "Database Endpoint: $DATABASE_ENDPOINT"
    echo "S3 Bucket: $S3_BUCKET_NAME"
    echo ""
    echo "🔧 Useful Commands:"
    echo "- View stack: aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION"
    echo "- View outputs: aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION --query 'Stacks[0].Outputs'"
    echo "- Delete stack: aws cloudformation delete-stack --stack-name $STACK_NAME --region $REGION"
    echo ""
    echo "📊 Monitoring:"
    echo "- CloudWatch Dashboard: https://console.aws.amazon.com/cloudwatch/home?region=$REGION#dashboards:name=BV-Backend-Dashboard"
    echo "- CloudWatch Logs: https://console.aws.amazon.com/cloudwatch/home?region=$REGION#logsV2:log-groups"
}

# Main deployment function
main() {
    log_info "Starting AWS deployment for Brahma Vastu Backend..."
    
    check_prerequisites
    create_parameters_file
    validate_template
    deploy_infrastructure
    get_stack_outputs
    create_deployment_package
    deploy_application
    setup_monitoring
    cleanup
    show_deployment_info
}

# Handle script arguments
case "${1:-deploy}" in
    deploy)
        main
        ;;
    destroy)
        log_info "Destroying infrastructure..."
        aws cloudformation delete-stack --stack-name "$STACK_NAME" --region "$REGION"
        log_success "Stack deletion initiated"
        ;;
    status)
        log_info "Checking stack status..."
        aws cloudformation describe-stacks --stack-name "$STACK_NAME" --region "$REGION" --query 'Stacks[0].StackStatus' --output text
        ;;
    outputs)
        log_info "Getting stack outputs..."
        aws cloudformation describe-stacks --stack-name "$STACK_NAME" --region "$REGION" --query 'Stacks[0].Outputs' --output table
        ;;
    *)
        echo "Usage: $0 [deploy|destroy|status|outputs]"
        echo ""
        echo "Commands:"
        echo "  deploy   - Deploy the infrastructure and application"
        echo "  destroy  - Destroy the infrastructure"
        echo "  status   - Check the stack status"
        echo "  outputs  - Show stack outputs"
        exit 1
        ;;
esac
