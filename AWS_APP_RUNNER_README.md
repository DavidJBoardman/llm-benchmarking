# AWS App Runner Deployment

## Important: Python Version Requirement

AWS App Runner requires **Python 3.11** for this application. Make sure your `apprunner.yaml` file specifies:

```yaml
version: 1.0
runtime: python3.11
```

## Quick Start

1. Push your code to a Git repository (GitHub, BitBucket, etc.)
2. Log in to the AWS Management Console
3. Navigate to AWS App Runner
4. Create a new service
5. Connect to your repository
6. Choose "Configuration file" and select `apprunner.yaml`
7. Set the required environment variables
8. Deploy

## Troubleshooting Build Failures

If you encounter build failures, try these solutions:

1. **Use the simplified configuration**:
   - Rename `apprunner.simple.yaml` to `apprunner.yaml`
   - This uses a minimal configuration that should work in most cases

2. **Manual configuration**:
   - Instead of using the configuration file, choose "Configuration values"
   - Set:
     - Runtime: Python 3.11
     - Build command: `pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt`
     - Start command: `streamlit run 1_Dashboard.py --server.port=8080 --server.address=0.0.0.0`
     - Port: 8080

3. **Check logs**:
   - Review the build logs for specific error messages
   - Common issues include missing dependencies or permission problems

## Environment Variables

Make sure to set these environment variables in the App Runner console:

```
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=your_db_password
POSTGRES_HOST=your_db_host.region.rds.amazonaws.com
POSTGRES_PORT=5432
POSTGRES_DB=your_db_name
INIT_DB=true
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=your_region
S3_BUCKET_NAME=your_bucket_name
USE_S3_STORAGE=true
```

## Database Access

Ensure your RDS database security group allows connections from App Runner. You may need to:

1. Find the IP ranges for App Runner in your region
2. Add these IP ranges to your RDS security group's inbound rules
3. Or use VPC connectors to establish a secure connection

## After Deployment

1. Set `INIT_DB=false` to prevent reinitializing the database on subsequent deployments
2. Test all features of the application
3. Set up auto-scaling if needed

For more detailed instructions, see `APP_RUNNER_DEPLOYMENT.md`. 