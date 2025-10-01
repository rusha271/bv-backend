#!/bin/bash

# AWS Monitoring Setup Script for Brahma Vastu Backend
# This script sets up CloudWatch monitoring, alarms, and dashboards

set -e

# Configuration
STACK_NAME="bv-backend-infrastructure"
REGION="us-east-1"
SNS_TOPIC_ARN="arn:aws:sns:us-east-1:123456789012:bv-backend-alerts"

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

# Create SNS topic for alerts
create_sns_topic() {
    log_info "Creating SNS topic for alerts..."
    
    # Check if topic exists
    if aws sns get-topic-attributes --topic-arn "$SNS_TOPIC_ARN" --region "$REGION" &> /dev/null; then
        log_info "SNS topic already exists"
    else
        aws sns create-topic --name "bv-backend-alerts" --region "$REGION"
        log_success "SNS topic created"
    fi
}

# Install CloudWatch agent on instances
install_cloudwatch_agent() {
    log_info "Installing CloudWatch agent on instances..."
    
    # Get Auto Scaling Group name
    ASG_NAME=$(aws cloudformation describe-stacks --stack-name "$STACK_NAME" --region "$REGION" --query 'Stacks[0].Outputs[?OutputKey==`AutoScalingGroupName`].OutputValue' --output text)
    
    # Get instance IDs
    INSTANCE_IDS=$(aws autoscaling describe-auto-scaling-groups --auto-scaling-group-names "$ASG_NAME" --region "$REGION" --query 'AutoScalingGroups[0].Instances[].InstanceId' --output text)
    
    for INSTANCE_ID in $INSTANCE_IDS; do
        log_info "Installing CloudWatch agent on instance: $INSTANCE_ID"
        
        # Install CloudWatch agent
        aws ssm send-command \
            --instance-ids "$INSTANCE_ID" \
            --document-name "AmazonCloudWatch-ManageAgent" \
            --parameters 'action=install' \
            --region "$REGION" \
            --output text
        
        # Configure CloudWatch agent
        aws ssm send-command \
            --instance-ids "$INSTANCE_ID" \
            --document-name "AmazonCloudWatch-ConfigureAgent" \
            --parameters "configLocation=file://cloudwatch-config.json" \
            --region "$REGION" \
            --output text
    done
    
    log_success "CloudWatch agent installation initiated"
}

# Create CloudWatch alarms
create_cloudwatch_alarms() {
    log_info "Creating CloudWatch alarms..."
    
    # Get stack outputs
    LOAD_BALANCER_ARN=$(aws cloudformation describe-stacks --stack-name "$STACK_NAME" --region "$REGION" --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerDNS`].OutputValue' --output text)
    DATABASE_IDENTIFIER=$(aws cloudformation describe-stacks --stack-name "$STACK_NAME" --region "$REGION" --query 'Stacks[0].Outputs[?OutputKey==`DatabaseEndpoint`].OutputValue' --output text)
    
    # Create alarms from JSON file
    if [ -f "deployment/alarms.json" ]; then
        jq -r '.alarms[]' deployment/alarms.json | while read -r alarm; do
            ALARM_NAME=$(echo "$alarm" | jq -r '.AlarmName')
            ALARM_DESCRIPTION=$(echo "$alarm" | jq -r '.AlarmDescription')
            METRIC_NAME=$(echo "$alarm" | jq -r '.MetricName')
            NAMESPACE=$(echo "$alarm" | jq -r '.Namespace')
            STATISTIC=$(echo "$alarm" | jq -r '.Statistic')
            PERIOD=$(echo "$alarm" | jq -r '.Period')
            EVALUATION_PERIODS=$(echo "$alarm" | jq -r '.EvaluationPeriods')
            THRESHOLD=$(echo "$alarm" | jq -r '.Threshold')
            COMPARISON_OPERATOR=$(echo "$alarm" | jq -r '.ComparisonOperator')
            
            # Create alarm
            aws cloudwatch put-metric-alarm \
                --alarm-name "$ALARM_NAME" \
                --alarm-description "$ALARM_DESCRIPTION" \
                --metric-name "$METRIC_NAME" \
                --namespace "$NAMESPACE" \
                --statistic "$STATISTIC" \
                --period "$PERIOD" \
                --evaluation-periods "$EVALUATION_PERIODS" \
                --threshold "$THRESHOLD" \
                --comparison-operator "$COMPARISON_OPERATOR" \
                --alarm-actions "$SNS_TOPIC_ARN" \
                --ok-actions "$SNS_TOPIC_ARN" \
                --region "$REGION"
        done
        
        log_success "CloudWatch alarms created"
    else
        log_warning "Alarms configuration file not found"
    fi
}

# Create CloudWatch dashboard
create_cloudwatch_dashboard() {
    log_info "Creating CloudWatch dashboard..."
    
    # Get stack outputs
    LOAD_BALANCER_DNS=$(aws cloudformation describe-stacks --stack-name "$STACK_NAME" --region "$REGION" --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerDNS`].OutputValue' --output text)
    
    # Create dashboard JSON
    cat > deployment/dashboard.json << EOF
{
    "widgets": [
        {
            "type": "metric",
            "x": 0,
            "y": 0,
            "width": 12,
            "height": 6,
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
                "title": "Application Load Balancer Metrics",
                "yAxis": {
                    "left": {
                        "min": 0
                    }
                }
            }
        },
        {
            "type": "metric",
            "x": 12,
            "y": 0,
            "width": 12,
            "height": 6,
            "properties": {
                "metrics": [
                    ["CWAgent", "cpu_usage_idle", "InstanceId", "*"],
                    ["CWAgent", "cpu_usage_user", "InstanceId", "*"],
                    ["CWAgent", "cpu_usage_system", "InstanceId", "*"]
                ],
                "period": 300,
                "stat": "Average",
                "region": "$REGION",
                "title": "CPU Utilization",
                "yAxis": {
                    "left": {
                        "min": 0,
                        "max": 100
                    }
                }
            }
        },
        {
            "type": "metric",
            "x": 0,
            "y": 6,
            "width": 12,
            "height": 6,
            "properties": {
                "metrics": [
                    ["CWAgent", "mem_used_percent", "InstanceId", "*"]
                ],
                "period": 300,
                "stat": "Average",
                "region": "$REGION",
                "title": "Memory Utilization",
                "yAxis": {
                    "left": {
                        "min": 0,
                        "max": 100
                    }
                }
            }
        },
        {
            "type": "metric",
            "x": 12,
            "y": 6,
            "width": 12,
            "height": 6,
            "properties": {
                "metrics": [
                    ["CWAgent", "disk_used_percent", "InstanceId", "*"]
                ],
                "period": 300,
                "stat": "Average",
                "region": "$REGION",
                "title": "Disk Utilization",
                "yAxis": {
                    "left": {
                        "min": 0,
                        "max": 100
                    }
                }
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
    
    log_success "CloudWatch dashboard created"
}

# Setup log groups
setup_log_groups() {
    log_info "Setting up CloudWatch log groups..."
    
    # Create log groups
    aws logs create-log-group --log-group-name "/aws/ec2/bv-backend/nginx/access" --region "$REGION" || true
    aws logs create-log-group --log-group-name "/aws/ec2/bv-backend/nginx/error" --region "$REGION" || true
    aws logs create-log-group --log-group-name "/aws/ec2/bv-backend/application" --region "$REGION" || true
    aws logs create-log-group --log-group-name "/aws/ec2/bv-backend/system" --region "$REGION" || true
    
    # Set retention policy
    aws logs put-retention-policy --log-group-name "/aws/ec2/bv-backend/nginx/access" --retention-in-days 30 --region "$REGION"
    aws logs put-retention-policy --log-group-name "/aws/ec2/bv-backend/nginx/error" --retention-in-days 30 --region "$REGION"
    aws logs put-retention-policy --log-group-name "/aws/ec2/bv-backend/application" --retention-in-days 30 --region "$REGION"
    aws logs put-retention-policy --log-group-name "/aws/ec2/bv-backend/system" --retention-in-days 30 --region "$REGION"
    
    log_success "Log groups created and configured"
}

# Main setup function
main() {
    log_info "Setting up monitoring for Brahma Vastu Backend..."
    
    create_sns_topic
    install_cloudwatch_agent
    create_cloudwatch_alarms
    create_cloudwatch_dashboard
    setup_log_groups
    
    log_success "Monitoring setup completed!"
    echo ""
    echo "📊 Monitoring Information:"
    echo "- CloudWatch Dashboard: https://console.aws.amazon.com/cloudwatch/home?region=$REGION#dashboards:name=BV-Backend-Dashboard"
    echo "- CloudWatch Logs: https://console.aws.amazon.com/cloudwatch/home?region=$REGION#logsV2:log-groups"
    echo "- CloudWatch Alarms: https://console.aws.amazon.com/cloudwatch/home?region=$REGION#alarmsV2:"
    echo ""
    echo "🔔 SNS Topic: $SNS_TOPIC_ARN"
    echo "   Subscribe to this topic to receive alerts via email or SMS"
}

# Handle script arguments
case "${1:-setup}" in
    setup)
        main
        ;;
    cleanup)
        log_info "Cleaning up monitoring resources..."
        aws cloudwatch delete-dashboards --dashboard-names "BV-Backend-Dashboard" --region "$REGION" || true
        aws logs delete-log-group --log-group-name "/aws/ec2/bv-backend/nginx/access" --region "$REGION" || true
        aws logs delete-log-group --log-group-name "/aws/ec2/bv-backend/nginx/error" --region "$REGION" || true
        aws logs delete-log-group --log-group-name "/aws/ec2/bv-backend/application" --region "$REGION" || true
        aws logs delete-log-group --log-group-name "/aws/ec2/bv-backend/system" --region "$REGION" || true
        log_success "Monitoring cleanup completed"
        ;;
    *)
        echo "Usage: $0 [setup|cleanup]"
        echo ""
        echo "Commands:"
        echo "  setup   - Set up monitoring and alerting"
        echo "  cleanup - Remove monitoring resources"
        exit 1
        ;;
esac
