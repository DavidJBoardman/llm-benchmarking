# LLM Benchmarking Dashboard

A Streamlit dashboard for benchmarking and auditing LLM models.

## Features

- Dashboard for visualizing LLM performance metrics
- Chat interface for testing LLM models
- Audit system for evaluating and storing LLM responses
- Edit and delete functionality for audit entries
- Database storage for persistent data
- S3 integration for file storage

## Local Development

### Prerequisites

- Python 3.10+
- PostgreSQL database
- Docker (optional)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/llm-benchmarking-dashboard.git
   cd llm-benchmarking-dashboard
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your configuration:
   ```
   POSTGRES_USER=your_db_user
   POSTGRES_PASSWORD=your_db_password
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   POSTGRES_DB=your_db_name
   INIT_DB=true
   
   # AWS S3 Configuration (optional)
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   AWS_REGION=your_region
   S3_BUCKET_NAME=your_bucket_name
   USE_S3_STORAGE=true  # Set to false to use local storage
   ```

5. Run the application:
   ```bash
   streamlit run 1_Dashboard.py
   ```

## Docker Deployment

### Using Docker Compose

1. Make sure Docker and Docker Compose are installed
2. Create a `.env` file as described above
3. Run the application with Docker Compose:
   ```bash
   docker-compose up --build
   ```
4. Access the application at http://localhost:8080

### Testing Docker Deployment

We've included a script to test the Docker deployment before deploying to AWS App Runner:

```bash
./test_app_locally.sh
```

This script will:
1. Build and start the Docker container
2. Check if the application is healthy
3. Test the database connection
4. Report any issues

## AWS App Runner Deployment

This application is ready to be deployed to AWS App Runner. We've included:

- `apprunner.yaml` - Configuration file for AWS App Runner
- `AWS_DEPLOYMENT.md` - Comprehensive deployment guide

To deploy to AWS App Runner:

1. Push your code to a GitHub repository
2. Follow the instructions in `AWS_DEPLOYMENT.md`

## Deploying to AWS

This application can be deployed to AWS using Docker and AWS App Runner. The deployment process is automated using the provided script.

### Prerequisites

1. Install and configure the AWS CLI:
   ```bash
   pip install awscli
   aws configure  # Enter your AWS credentials
   ```

2. Make sure you have Docker installed and running on your machine.

3. Ensure you have the necessary IAM permissions to:
   - Create and push to ECR repositories
   - Create and update App Runner services
   - Create IAM roles (or use existing ones)

### Deployment Steps

1. Make sure your `.env` file is properly configured with your database and S3 credentials.

2. Run the deployment script:
   ```bash
   ./deploy_to_aws.sh
   ```

3. The script will:
   - Build your Docker image
   - Push it to Amazon ECR
   - Create or update an App Runner service
   - Display the URL where your application is deployed

### Customizing the Deployment

You can customize the deployment by editing the `deploy_to_aws.sh` script:

- Change the AWS region
- Modify the ECR repository name
- Change the App Runner service name
- Adjust the instance configuration (CPU/memory)

### Troubleshooting

If you encounter issues during deployment:

1. Check that your AWS credentials are correctly configured
2. Ensure you have the necessary IAM permissions
3. Verify that your Docker image builds and runs locally
4. Check the AWS App Runner console for service logs

## Database Schema

The application uses the following database tables:

- `chat_audits` - Stores audit records of LLM interactions
- `gpu_models` - Stores available GPU models
- `llm_models` - Stores available LLM models

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Deployment

### Local Deployment with Docker

For local deployment using Docker:

1. Make sure Docker is installed and running on your machine
   - See [Docker Setup Guide](DOCKER_SETUP.md) for installation instructions

2. Build and run the Docker container:
   ```bash
   docker build -t scenegraph-studios-benchmarks .
   docker run -p 8501:8501 --env-file .env scenegraph-studios-benchmarks
   ```

3. Access the application at http://localhost:8501

### AWS Deployment

For deploying to AWS:

1. Follow the [AWS Deployment Guide](AWS_DEPLOYMENT.md) for detailed instructions
2. Or use the quick deployment script:
   ```bash
   ./deploy_to_aws.sh
   ``` 