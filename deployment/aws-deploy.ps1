# AWS Deployment Script for Brahma Vastu Backend (PowerShell)
# This script automates the deployment of the infrastructure and application

param(
    [Parameter(Position=0)]
    [ValidateSet("deploy", "destroy", "status", "outputs")]
    [string]$Action = "deploy",
    
    [string]$StackName = "bv-backend-infrastructure",
    [string]$Region = "us-east-1",
    [string]$TemplateFile = "deployment/aws-cloudformation.yaml",
    [string]$KeyPairName = "bv-backend-keypair",
    [string]$InstanceType = "t3.medium",
    [string]$DBInstanceClass = "db.t3.micro",
    [string]$Environment = "production"
)

# Configuration
$ParametersFile = "deployment/aws-parameters.json"

# Functions
function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Check prerequisites
function Test-Prerequisites {
    Write-Info "Checking prerequisites..."
    
    # Check if AWS CLI is installed
    if (-not (Get-Command aws -ErrorAction SilentlyContinue)) {
        Write-Error "AWS CLI is not installed. Please install it first."
        exit 1
    }
    
    # Check if AWS CLI is configured
    try {
        aws sts get-caller-identity | Out-Null
    }
    catch {
        Write-Error "AWS CLI is not configured. Please run 'aws configure' first."
        exit 1
    }
    
    Write-Success "Prerequisites check passed"
}

# Create parameters file
function New-ParametersFile {
    Write-Info "Creating parameters file..."
    
    $dbPassword = [System.Web.Security.Membership]::GeneratePassword(32, 8)
    
    $parameters = @(
        @{
            ParameterKey = "KeyPairName"
            ParameterValue = $KeyPairName
        },
        @{
            ParameterKey = "InstanceType"
            ParameterValue = $InstanceType
        },
        @{
            ParameterKey = "DBInstanceClass"
            ParameterValue = $DBInstanceClass
        },
        @{
            ParameterKey = "DBUsername"
            ParameterValue = "admin"
        },
        @{
            ParameterKey = "DBPassword"
            ParameterValue = $dbPassword
        },
        @{
            ParameterKey = "Environment"
            ParameterValue = $Environment
        }
    )
    
    $parameters | ConvertTo-Json -Depth 3 | Out-File -FilePath $ParametersFile -Encoding UTF8
    
    Write-Success "Parameters file created: $ParametersFile"
}

# Validate CloudFormation template
function Test-Template {
    Write-Info "Validating CloudFormation template..."
    
    try {
        aws cloudformation validate-template --template-body "file://$TemplateFile" --region $Region | Out-Null
        Write-Success "CloudFormation template is valid"
    }
    catch {
        Write-Error "CloudFormation template validation failed"
        exit 1
    }
}

# Deploy infrastructure
function Deploy-Infrastructure {
    Write-Info "Deploying infrastructure..."
    
    # Check if stack exists
    try {
        aws cloudformation describe-stacks --stack-name $StackName --region $Region | Out-Null
        Write-Info "Stack exists, updating..."
        
        aws cloudformation update-stack `
            --stack-name $StackName `
            --template-body "file://$TemplateFile" `
            --parameters "file://$ParametersFile" `
            --capabilities CAPABILITY_IAM `
            --region $Region
        
        Write-Info "Waiting for stack update to complete..."
        aws cloudformation wait stack-update-complete --stack-name $StackName --region $Region
    }
    catch {
        Write-Info "Creating new stack..."
        
        aws cloudformation create-stack `
            --stack-name $StackName `
            --template-body "file://$TemplateFile" `
            --parameters "file://$ParametersFile" `
            --capabilities CAPABILITY_IAM `
            --region $Region
        
        Write-Info "Waiting for stack creation to complete..."
        aws cloudformation wait stack-create-complete --stack-name $StackName --region $Region
    }
    
    Write-Success "Infrastructure deployment completed"
}

# Get stack outputs
function Get-StackOutputs {
    Write-Info "Getting stack outputs..."
    
    $outputs = aws cloudformation describe-stacks --stack-name $StackName --region $Region --query 'Stacks[0].Outputs' --output json | ConvertFrom-Json
    
    $script:LoadBalancerDNS = ($outputs | Where-Object { $_.OutputKey -eq "LoadBalancerDNS" }).OutputValue
    $script:DatabaseEndpoint = ($outputs | Where-Object { $_.OutputKey -eq "DatabaseEndpoint" }).OutputValue
    $script:S3BucketName = ($outputs | Where-Object { $_.OutputKey -eq "S3BucketName" }).OutputValue
    
    Write-Success "Stack outputs retrieved"
    Write-Info "Load Balancer DNS: $LoadBalancerDNS"
    Write-Info "Database Endpoint: $DatabaseEndpoint"
    Write-Info "S3 Bucket: $S3BucketName"
}

# Create deployment package
function New-DeploymentPackage {
    Write-Info "Creating deployment package..."
    
    # Create deployment directory
    $DeployDir = "deployment/package"
    New-Item -ItemType Directory -Path $DeployDir -Force | Out-Null
    
    # Copy application files
    Copy-Item -Path "app" -Destination "$DeployDir/" -Recurse -Force
    Copy-Item -Path "alembic" -Destination "$DeployDir/" -Recurse -Force
    Copy-Item -Path "requirements.txt" -Destination "$DeployDir/" -Force
    Copy-Item -Path "alembic.ini" -Destination "$DeployDir/" -Force
    Copy-Item -Path "Dockerfile" -Destination "$DeployDir/" -Force
    Copy-Item -Path "docker-compose.yml" -Destination "$DeployDir/" -Force
    Copy-Item -Path "nginx.conf" -Destination "$DeployDir/" -Force
    
    # Create deployment script
    $deployScript = @'
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
'@
    
    $deployScript | Out-File -FilePath "$DeployDir/deploy.sh" -Encoding UTF8
    
    # Create zip package
    Compress-Archive -Path "$DeployDir/*" -DestinationPath "deployment/bv-backend-deployment.zip" -Force
    
    Write-Success "Deployment package created: deployment/bv-backend-deployment.zip"
}

# Setup monitoring
function Set-Monitoring {
    Write-Info "Setting up monitoring..."
    
    # Create CloudWatch dashboard
    $dashboard = @{
        widgets = @(
            @{
                type = "metric"
                properties = @{
                    metrics = @(
                        @("AWS/ApplicationELB", "TargetResponseTime", "LoadBalancer", $LoadBalancerDNS),
                        @("AWS/ApplicationELB", "RequestCount", "LoadBalancer", $LoadBalancerDNS),
                        @("AWS/ApplicationELB", "HTTPCode_Target_2XX_Count", "LoadBalancer", $LoadBalancerDNS),
                        @("AWS/ApplicationELB", "HTTPCode_Target_4XX_Count", "LoadBalancer", $LoadBalancerDNS),
                        @("AWS/ApplicationELB", "HTTPCode_Target_5XX_Count", "LoadBalancer", $LoadBalancerDNS)
                    )
                    period = 300
                    stat = "Average"
                    region = $Region
                    title = "Application Load Balancer Metrics"
                }
            }
        )
    }
    
    $dashboard | ConvertTo-Json -Depth 10 | Out-File -FilePath "deployment/dashboard.json" -Encoding UTF8
    
    # Create dashboard
    aws cloudwatch put-dashboard --dashboard-name "BV-Backend-Dashboard" --dashboard-body "file://deployment/dashboard.json" --region $Region
    
    Write-Success "Monitoring setup completed"
}

# Cleanup
function Remove-TempFiles {
    Write-Info "Cleaning up temporary files..."
    Remove-Item -Path $ParametersFile -Force -ErrorAction SilentlyContinue
    Remove-Item -Path "deployment/package" -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -Path "deployment/bv-backend-deployment.zip" -Force -ErrorAction SilentlyContinue
    Remove-Item -Path "deployment/dashboard.json" -Force -ErrorAction SilentlyContinue
    Write-Success "Cleanup completed"
}

# Show deployment information
function Show-DeploymentInfo {
    Write-Success "Deployment completed successfully!"
    Write-Host ""
    Write-Host "📋 Deployment Information:" -ForegroundColor Cyan
    Write-Host "Stack Name: $StackName"
    Write-Host "Region: $Region"
    Write-Host "Load Balancer URL: http://$LoadBalancerDNS"
    Write-Host "Database Endpoint: $DatabaseEndpoint"
    Write-Host "S3 Bucket: $S3BucketName"
    Write-Host ""
    Write-Host "🔧 Useful Commands:" -ForegroundColor Cyan
    Write-Host "- View stack: aws cloudformation describe-stacks --stack-name $StackName --region $Region"
    Write-Host "- View outputs: aws cloudformation describe-stacks --stack-name $StackName --region $Region --query 'Stacks[0].Outputs'"
    Write-Host "- Delete stack: aws cloudformation delete-stack --stack-name $StackName --region $Region"
    Write-Host ""
    Write-Host "📊 Monitoring:" -ForegroundColor Cyan
    Write-Host "- CloudWatch Dashboard: https://console.aws.amazon.com/cloudwatch/home?region=$Region#dashboards:name=BV-Backend-Dashboard"
    Write-Host "- CloudWatch Logs: https://console.aws.amazon.com/cloudwatch/home?region=$Region#logsV2:log-groups"
}

# Main deployment function
function Start-Deployment {
    Write-Info "Starting AWS deployment for Brahma Vastu Backend..."
    
    Test-Prerequisites
    New-ParametersFile
    Test-Template
    Deploy-Infrastructure
    Get-StackOutputs
    New-DeploymentPackage
    Set-Monitoring
    Remove-TempFiles
    Show-DeploymentInfo
}

# Handle script actions
switch ($Action) {
    "deploy" {
        Start-Deployment
    }
    "destroy" {
        Write-Info "Destroying infrastructure..."
        aws cloudformation delete-stack --stack-name $StackName --region $Region
        Write-Success "Stack deletion initiated"
    }
    "status" {
        Write-Info "Checking stack status..."
        aws cloudformation describe-stacks --stack-name $StackName --region $Region --query 'Stacks[0].StackStatus' --output text
    }
    "outputs" {
        Write-Info "Getting stack outputs..."
        aws cloudformation describe-stacks --stack-name $StackName --region $Region --query 'Stacks[0].Outputs' --output table
    }
    default {
        Write-Host "Usage: .\aws-deploy.ps1 [deploy|destroy|status|outputs]"
        Write-Host ""
        Write-Host "Commands:"
        Write-Host "  deploy   - Deploy the infrastructure and application"
        Write-Host "  destroy  - Destroy the infrastructure"
        Write-Host "  status   - Check the stack status"
        Write-Host "  outputs  - Show stack outputs"
        exit 1
    }
}
