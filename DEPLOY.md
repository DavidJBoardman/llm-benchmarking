# Deploying the LLM Benchmark Dashboard to AWS

This guide explains how to deploy the LLM Benchmark Dashboard to AWS using Docker, Amazon ECR, and AWS App Runner.

## Prerequisites

1. **AWS CLI**: Install and configure the AWS CLI with appropriate permissions.
   ```bash
   pip install awscli
   aws configure
   ```

2. **Docker**: Install Docker on your local machine.
   - [Docker Desktop](https://www.docker.com/products/docker-desktop) for Windows/Mac
   - [Docker Engine](https://docs.docker.com/engine/install/) for Linux

3. **IAM Roles**: Ensure you have the following IAM roles in your AWS account:
   - `AppRunnerECRAccessRole`: Allows App Runner to pull images from ECR
   - `AppRunnerServiceRole`: Allows App Runner to run the service

## Environment Variables

Create a `.env` file based on the `.env.example` template. This file contains sensitive information and should not be committed to version control.

For AWS deployment, you'll need to set up the following environment variables:
- Database connection details (if using a database)
- AWS credentials for S3 access (if using S3 for storage)
- Other application-specific settings

## Deployment Steps

### 1. Make the deployment script executable

```bash
chmod +x deploy_to_aws.sh
```

### 2. Run the deployment script

```bash
./deploy_to_aws.sh
```

This script will:
1. Build a Docker image of the application
2. Create an ECR repository (if it doesn't exist)
3. Push the Docker image to ECR
4. Create or update an App Runner service using the x86_64 (AMD64) architecture

### 3. Customizing the Deployment

You can customize the deployment by setting environment variables before running the script:

```bash
export AWS_REGION="us-west-2"
export ECR_REPOSITORY_NAME="my-custom-repo-name"
export APP_RUNNER_SERVICE_NAME="my-custom-service-name"
export IMAGE_TAG="v1.0.0"
./deploy_to_aws.sh
```

## Accessing the Application

After deployment, the App Runner service URL will be displayed in the AWS App Runner console. You can access your application at this URL.

## Troubleshooting

### Common Issues

1. **Authentication Failures**: Ensure your AWS CLI is properly configured with the correct credentials.
   ```bash
   aws sts get-caller-identity
   ```

2. **Missing IAM Roles**: If you encounter errors about missing roles, create them in the IAM console or use the following commands:
   ```bash
   aws iam create-role --role-name AppRunnerECRAccessRole --assume-role-policy-document file://apprunner-ecr-role-trust-policy.json
   aws iam create-role --role-name AppRunnerServiceRole --assume-role-policy-document file://apprunner-service-role-trust-policy.json
   ```

3. **Docker Build Failures**: Check your Dockerfile for errors and ensure all dependencies are properly specified.

4. **App Runner Service Creation Failures**: Check the AWS App Runner console for detailed error messages.

## Monitoring and Logs

- **CloudWatch Logs**: App Runner automatically sends logs to CloudWatch. You can view them in the CloudWatch console.
- **App Runner Console**: The App Runner console provides basic monitoring and logs for your service.

## Updating the Application

To update the application, simply run the deployment script again. It will build a new Docker image, push it to ECR, and update the App Runner service.

## Cleaning Up

To delete the App Runner service and ECR repository:

```bash
aws apprunner delete-service --service-arn <service-arn>
aws ecr delete-repository --repository-name <repository-name> --force
``` 