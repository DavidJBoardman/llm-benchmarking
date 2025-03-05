# Docker Deployment Guide

This guide provides instructions for deploying the LLM Benchmarking Dashboard using Docker.

## Prerequisites

1. Docker and Docker Compose installed on your system
2. Access to a PostgreSQL database (can be local or remote)
3. (Optional) AWS S3 bucket for file storage

## Local Development with Docker

### 1. Environment Setup

Make sure your `.env` file is properly configured with the following variables:

```
POSTGRES_URI=postgresql+psycopg2://username:password@hostname:port/database
POSTGRES_USER=username
POSTGRES_PASSWORD=password
POSTGRES_HOST=hostname
POSTGRES_PORT=5432
POSTGRES_DB=database_name
INIT_DB=false  # Set to "true" to initialize the database with sample data

# AWS S3 Configuration (optional)
AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-s3-bucket-name
USE_S3_STORAGE=true  # Set to "false" to use local storage instead of S3
```

### 2. Building and Running with Docker Compose

To build and run the application using Docker Compose:

```bash
docker-compose up --build
```

This will start the application on port 8080. You can access it at http://localhost:8080

### 3. Building and Testing with Script

Alternatively, you can use the provided script to build and test the Docker image:

```bash
./build_and_test.sh
```

This script will:
1. Build the Docker image
2. Run a container from the image
3. Check if the application is healthy
4. Display the container logs

## Preparing for AWS App Runner Deployment

The Docker configuration in this project is optimized for AWS App Runner deployment. The key files are:

1. `Dockerfile` - Defines the container image
2. `apprunner.yaml` - Configuration for AWS App Runner

### Testing the App Runner Configuration Locally

To test the App Runner configuration locally:

```bash
docker build -t llm-benchmarking-dashboard .
docker run -p 8080:8080 --env-file .env llm-benchmarking-dashboard
```

## Troubleshooting

### Database Connection Issues

If you encounter database connection issues:

1. Ensure your database credentials in the `.env` file are correct
2. If using a remote database, make sure it's accessible from your Docker container
3. Check the container logs for specific error messages:
   ```bash
   docker logs <container_id>
   ```

### Port Conflicts

If port 8080 is already in use:

1. Change the port mapping in `docker-compose.yml`:
   ```yaml
   ports:
     - "8081:8080"  # Map container port 8080 to host port 8081
   ```

2. Or stop the service using that port:
   ```bash
   sudo lsof -i :8080  # Find the process using port 8080
   sudo kill <PID>     # Kill the process
   ```

## Cleaning Up

To stop and remove containers, networks, and volumes:

```bash
docker-compose down
```

To remove the built image:

```bash
docker rmi llm-benchmarking-dashboard
``` 