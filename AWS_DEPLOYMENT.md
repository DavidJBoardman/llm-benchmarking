# Deploying to AWS App Runner

This guide provides step-by-step instructions for deploying the LLM Benchmarking Dashboard to AWS App Runner.

## Prerequisites

Before you begin, make sure you have:

1. An AWS account with permissions to create App Runner services
2. A PostgreSQL database (AWS RDS) set up and accessible
3. An S3 bucket for storing audio files
4. Your code pushed to a GitHub repository

## Deployment Steps

### 1. Prepare Your Repository

Make sure your code is pushed to a GitHub repository. App Runner can deploy directly from GitHub.

```bash
# If you haven't already set up Git
git init
git add .
git commit -m "Initial commit"

# Add your GitHub repository as a remote
git remote add origin https://github.com/yourusername/your-repo-name.git

# Push your code to GitHub
git push -u origin main
```

### 2. Deploy to AWS App Runner

#### Using the AWS Console

1. **Log in to the AWS Management Console**:
   - Go to https://console.aws.amazon.com/
   - Sign in with your AWS account credentials

2. **Navigate to AWS App Runner**:
   - In the search bar at the top, type "App Runner" and select it from the results

3. **Create a new App Runner service**:
   - Click on "Create service"
   - For source and deployment, choose "Source code repository"
   - Connect to your GitHub repository (you'll need to authorize AWS to access your GitHub account)
   - Select the repository containing your benchmarking application
   - Choose the branch you want to deploy (usually "main" or "master")

4. **Configure the build**:
   - For "Configuration source", select "Configuration file"
   - This will use the `apprunner.yaml` file in your repository

5. **Configure the service**:
   - Give your service a name (e.g., "llm-benchmarking-dashboard")
   - Choose an appropriate instance size (at least 1 vCPU and 2GB RAM recommended)
   - Under "Environment variables", add all the environment variables from your `.env` file:
     ```
     POSTGRES_USER=your_db_user
     POSTGRES_PASSWORD=your_db_password
     POSTGRES_HOST=your_db_host.region.rds.amazonaws.com
     POSTGRES_PORT=5432
     POSTGRES_DB=your_db_name
     INIT_DB=true  # Set to true for first deployment, then change to false
     AWS_ACCESS_KEY_ID=your_access_key
     AWS_SECRET_ACCESS_KEY=your_secret_key
     AWS_REGION=your_region
     S3_BUCKET_NAME=your_bucket_name
     USE_S3_STORAGE=true
     ```

6. **Configure networking**:
   - For most cases, the default settings are fine
   - If you need to access your RDS database, make sure the security group allows connections from App Runner

7. **Review and create**:
   - Review all settings
   - Click "Create & deploy"

#### Using the AWS CLI

If you prefer using the AWS CLI, you can deploy with the following commands:

```bash
# Create an App Runner service
aws apprunner create-service \
  --service-name llm-benchmarking-dashboard \
  --source-configuration '{
    "CodeRepository": {
      "RepositoryUrl": "https://github.com/yourusername/your-repo-name",
      "SourceCodeVersion": {
        "Type": "BRANCH",
        "Value": "main"
      },
      "CodeConfiguration": {
        "ConfigurationSource": "REPOSITORY",
        "ConfigurationValues": {
          "Runtime": "PYTHON_3",
          "BuildCommand": "pip install -r requirements.txt",
          "StartCommand": "streamlit run 1_Dashboard.py --server.port=8080 --server.address=0.0.0.0",
          "Port": "8080"
        }
      }
    }
  }' \
  --instance-configuration '{
    "Cpu": "1 vCPU",
    "Memory": "2 GB"
  }' \
  --environment-variables '[
    {"Name": "POSTGRES_USER", "Value": "your_db_user"},
    {"Name": "POSTGRES_PASSWORD", "Value": "your_db_password"},
    {"Name": "POSTGRES_HOST", "Value": "your_db_host.region.rds.amazonaws.com"},
    {"Name": "POSTGRES_PORT", "Value": "5432"},
    {"Name": "POSTGRES_DB", "Value": "your_db_name"},
    {"Name": "INIT_DB", "Value": "true"},
    {"Name": "AWS_ACCESS_KEY_ID", "Value": "your_access_key"},
    {"Name": "AWS_SECRET_ACCESS_KEY", "Value": "your_secret_key"},
    {"Name": "AWS_REGION", "Value": "your_region"},
    {"Name": "S3_BUCKET_NAME", "Value": "your_bucket_name"},
    {"Name": "USE_S3_STORAGE", "Value": "true"}
  ]'
```

## After Deployment

After your application is deployed, there are a few things to check:

1. **Test the application**:
   - Visit the provided URL to make sure your application is working correctly
   - Test the audit features, including the new edit and delete functionality

2. **Check the logs**:
   - If there are any issues, check the App Runner logs for error messages
   - In the App Runner console, select your service and click on "Logs"

3. **Update environment variables**:
   - After the first successful deployment, change `INIT_DB` from `true` to `false` to prevent reinitializing the database on subsequent deployments

4. **Set up auto-scaling (optional)**:
   - If you expect high traffic, configure auto-scaling in the App Runner settings

## Troubleshooting

### Database Connection Issues

If you encounter database connection issues:

1. **Check security groups**:
   - Make sure your RDS security group allows incoming connections from App Runner
   - You may need to add the App Runner service's security group to your RDS inbound rules

2. **Verify environment variables**:
   - Double-check that all database connection environment variables are correctly set

3. **Check network ACLs**:
   - Ensure your VPC network ACLs allow traffic between App Runner and RDS

### Application Errors

If the application fails to start:

1. **Check App Runner logs**:
   - Review the logs for any error messages

2. **Verify apprunner.yaml**:
   - Make sure your apprunner.yaml file is correctly formatted

3. **Test locally with Docker**:
   - Run the application locally using Docker to verify it works before deploying

## Security Considerations

1. **Environment Variables**:
   - Store sensitive information like database credentials and AWS access keys in AWS Secrets Manager or Parameter Store
   - Use IAM roles instead of access keys when possible

2. **Database Access**:
   - Use a dedicated database user with minimal permissions
   - Consider using AWS RDS Proxy for improved security

3. **S3 Access**:
   - Configure your S3 bucket with appropriate access controls
   - Use IAM roles with least privilege principles

## Maintenance

1. **Updates**:
   - When you push changes to your GitHub repository, App Runner can automatically redeploy your application
   - Configure automatic deployments in the App Runner settings

2. **Monitoring**:
   - Set up CloudWatch alarms to monitor your application's performance
   - Configure notifications for any issues

3. **Backups**:
   - Regularly back up your RDS database
   - Consider enabling point-in-time recovery 