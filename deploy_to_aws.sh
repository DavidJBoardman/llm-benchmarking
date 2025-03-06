#!/bin/bash
set -e

# Configuration
AWS_REGION=${AWS_REGION:-"eu-west-2"}
ECR_REPOSITORY_NAME=${ECR_REPOSITORY_NAME:-"scenegraph-studios-benchmark-dashboard"}
APP_RUNNER_SERVICE_NAME=${APP_RUNNER_SERVICE_NAME:-"scenegraph-studios-benchmark-dashboard"}
IMAGE_TAG=${IMAGE_TAG:-"latest"}

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "AWS CLI is not installed. Please install it first."
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Please install it first."
    exit 1
fi

# Get AWS account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
if [ $? -ne 0 ]; then
    echo "Failed to get AWS account ID. Make sure you're authenticated with AWS CLI."
    exit 1
fi

# ECR repository URI
ECR_REPOSITORY_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY_NAME}"

echo "=== Building and deploying to AWS ==="
echo "AWS Region: ${AWS_REGION}"
echo "ECR Repository: ${ECR_REPOSITORY_NAME}"
echo "App Runner Service: ${APP_RUNNER_SERVICE_NAME}"
echo "Image Tag: ${IMAGE_TAG}"
echo "ECR Repository URI: ${ECR_REPOSITORY_URI}"
echo "Architecture: x86_64 (AMD64)"

# Create ECR repository if it doesn't exist
echo "=== Creating ECR repository if it doesn't exist ==="
aws ecr describe-repositories --repository-names ${ECR_REPOSITORY_NAME} --region ${AWS_REGION} || \
    aws ecr create-repository --repository-name ${ECR_REPOSITORY_NAME} --region ${AWS_REGION}

# Authenticate Docker with ECR
echo "=== Authenticating Docker with ECR ==="
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REPOSITORY_URI}

# Build Docker image for x86_64 (AMD64) architecture
echo "=== Building Docker image for x86_64 (AMD64) architecture ==="
docker build --platform=linux/amd64 -t ${ECR_REPOSITORY_NAME}:${IMAGE_TAG} .

# Tag Docker image
echo "=== Tagging Docker image ==="
docker tag ${ECR_REPOSITORY_NAME}:${IMAGE_TAG} ${ECR_REPOSITORY_URI}:${IMAGE_TAG}

# Push Docker image to ECR
echo "=== Pushing Docker image to ECR ==="
docker push ${ECR_REPOSITORY_URI}:${IMAGE_TAG}

# Check if App Runner service exists
SERVICE_ARN=$(aws apprunner list-services --region ${AWS_REGION} --query "ServiceSummaryList[?ServiceName=='${APP_RUNNER_SERVICE_NAME}'].ServiceArn" --output text)

# Create JSON configuration files for App Runner
cat > source-config.json << EOF
{
  "AuthenticationConfiguration": {
    "AccessRoleArn": "arn:aws:iam::${AWS_ACCOUNT_ID}:role/service-role/AppRunnerECRAccessRole"
  },
  "AutoDeploymentsEnabled": true,
  "ImageRepository": {
    "ImageIdentifier": "${ECR_REPOSITORY_URI}:${IMAGE_TAG}",
    "ImageConfiguration": {
      "Port": "8501",
      "RuntimeEnvironmentVariables": {
        "ENABLE_HEALTH_CHECK": "true",
        "STREAMLIT_SERVER_ENABLE_CORS": "false",
        "STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION": "false",
        "STREAMLIT_SERVER_ENABLE_WEBSOCKET_COMPRESSION": "false",
        "STREAMLIT_SERVER_HEADLESS": "true"
      }
    },
    "ImageRepositoryType": "ECR"
  }
}
EOF

cat > instance-config.json << EOF
{
  "Cpu": "1 vCPU",
  "Memory": "2 GB",
  "InstanceRoleArn": "arn:aws:iam::${AWS_ACCOUNT_ID}:role/service-role/AppRunnerServiceRole"
}
EOF

cat > health-check-config.json << EOF
{
  "Protocol": "HTTP",
  "Path": "/_stcore/health",
  "Interval": 20,
  "Timeout": 5,
  "HealthyThreshold": 1,
  "UnhealthyThreshold": 5
}
EOF

cat > network-config.json << EOF
{
  "IngressConfiguration": {
    "IsPubliclyAccessible": true
  },
  "EgressConfiguration": {
    "EgressType": "DEFAULT"
  },
  "IpAddressType": "IPV4"
}
EOF

if [ -z "$SERVICE_ARN" ]; then
    # Create App Runner service
    echo "=== Creating App Runner service ==="
    aws apprunner create-service \
        --service-name ${APP_RUNNER_SERVICE_NAME} \
        --source-configuration file://source-config.json \
        --instance-configuration file://instance-config.json \
        --health-check-configuration file://health-check-config.json \
        --network-configuration file://network-config.json \
        --region ${AWS_REGION}
else
    # Update App Runner service
    echo "=== Updating App Runner service ==="
    aws apprunner update-service \
        --service-arn ${SERVICE_ARN} \
        --source-configuration file://source-config.json \
        --health-check-configuration file://health-check-config.json \
        --region ${AWS_REGION}
fi

# Clean up temporary files
rm -f source-config.json instance-config.json health-check-config.json network-config.json

echo "=== Deployment completed ==="
echo "Check the AWS App Runner console for service status and URL." 