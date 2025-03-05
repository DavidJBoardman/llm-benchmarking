# AWS App Runner Deployment Guide

This is a simplified guide for deploying the LLM Benchmarking Dashboard to AWS App Runner.

## Quick Deployment Steps

1. **Log in to the AWS Management Console**
2. **Navigate to AWS App Runner**
3. **Create a new service**:
   - Source: Your code repository (GitHub/BitBucket)
   - Branch: main (or your preferred branch)
   - Configuration source: Repository (apprunner.yaml)

4. **Set Environment Variables**:
   - POSTGRES_USER=your_db_user
   - POSTGRES_PASSWORD=your_db_password
   - POSTGRES_HOST=your_db_host.region.rds.amazonaws.com
   - POSTGRES_PORT=5432
   - POSTGRES_DB=your_db_name
   - INIT_DB=true
   - AWS_ACCESS_KEY_ID=your_access_key
   - AWS_SECRET_ACCESS_KEY=your_secret_key
   - AWS_REGION=your_region
   - S3_BUCKET_NAME=your_bucket_name
   - USE_S3_STORAGE=true

5. **Deploy**

## Troubleshooting

### Build Failures

If you encounter build failures:

1. **Check the logs** in the AWS App Runner console
2. **Common issues**:
   - Missing system dependencies: The pre-build commands should install these
   - Python package installation failures: Try updating requirements.txt
   - Permission issues: Make sure your App Runner service has the necessary permissions

### Database Connection Issues

1. **Check security groups** on your RDS instance
2. **Verify environment variables** are correctly set
3. **Test connection** from another AWS service in the same region

### Application Startup Issues

1. **Check the logs** for specific error messages
2. **Verify port configuration** (should be 8080)
3. **Check health check endpoint** is correctly configured

## Manual Deployment (Alternative)

If you continue to have issues with the apprunner.yaml file, you can try manual configuration:

1. Choose "Configuration file" = "Configuration values"
2. Set:
   - Build command: `pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt`
   - Start command: `streamlit run 1_Dashboard.py --server.port=8080 --server.address=0.0.0.0`
   - Port: 8080

## After Deployment

1. After successful deployment, set `INIT_DB=false` to prevent reinitializing the database on subsequent deployments
2. Test all features of the application
3. Set up auto-scaling if needed 