# Deploying to AWS App Runner

This guide provides instructions for deploying the LLM Benchmarking Dashboard to AWS App Runner.

## Prerequisites

1. An AWS account with appropriate permissions
2. AWS CLI installed and configured
3. A PostgreSQL database (can be RDS or other managed service)
4. An S3 bucket for file storage (optional)

## Deployment Steps

### 1. Set up the PostgreSQL Database

1. Create a PostgreSQL database in AWS RDS or another service
2. Note the database credentials (hostname, username, password, database name)

### 2. Set up the S3 Bucket (Optional)

1. Create an S3 bucket for file storage
2. Set up appropriate IAM permissions for App Runner to access the bucket

### 3. Configure Environment Variables

In the AWS App Runner console, you'll need to set the following environment variables:

```
POSTGRES_USER=your_db_username
POSTGRES_PASSWORD=your_db_password
POSTGRES_HOST=your_db_hostname
POSTGRES_PORT=5432
POSTGRES_DB=your_db_name
INIT_DB=true  # Set to true for first deployment, then change to false

# Optional S3 Configuration
AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-s3-bucket-name
USE_S3_STORAGE=true  # Set to false to use local storage
```

### 4. Deploy to App Runner

1. Log in to the AWS Management Console
2. Navigate to AWS App Runner
3. Click "Create service"
4. Choose "Source code repository" and connect your GitHub repository
5. Select the repository and branch containing your code
6. Choose "Python 3" as the runtime
7. Set the build command to `pip install -r requirements.txt`
8. Set the start command to `streamlit run 1_Dashboard.py --server.port=8080 --server.address=0.0.0.0`
9. Set the port to 8080
10. Configure the environment variables as described above
11. Choose an appropriate instance size (at least 1 vCPU and 2GB RAM recommended)
12. Configure auto-scaling settings as needed
13. Click "Create & deploy"

Alternatively, you can use the `apprunner.yaml` file in this repository for configuration.

### 5. Access Your Application

Once deployment is complete, AWS App Runner will provide a URL to access your application.

## Troubleshooting

### Database Connection Issues

If you encounter database connection issues:

1. Ensure your RDS security group allows connections from App Runner
2. Verify that your database credentials are correct
3. Check the App Runner logs for specific error messages

### S3 Access Issues

If you encounter S3 access issues:

1. Verify that your IAM permissions are correctly set up
2. Check that your AWS credentials are correct
3. Ensure the S3 bucket exists in the specified region

## Updating Your Application

To update your application:

1. Push changes to your GitHub repository
2. AWS App Runner will automatically detect changes and redeploy

## Monitoring

AWS App Runner provides basic monitoring through CloudWatch. You can:

1. View logs in the App Runner console
2. Set up CloudWatch alarms for metrics like CPU and memory usage
3. Configure health checks to ensure your application is running properly 