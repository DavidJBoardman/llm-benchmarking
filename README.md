# LLM Benchmark Dashboard

A comprehensive dashboard for visualizing and comparing LLM benchmark performance across different GPUs and models.

## Features

- Performance metrics comparison across different GPUs and models
- Detailed visualization of GPU resource usage over time
- Chat log viewer for examining model responses
- Chat audit system for evaluating response quality
- Audit history tracking and statistics
- **Custom GPU and Model Support**: Add and track custom GPU and model configurations
- **S3 Integration**: Store and read logs and benchmark data from Amazon S3

## Prerequisites

- Python 3.8+
- Docker and Docker Compose (for containerized deployment)
- PostgreSQL database (for audit features)
- AWS S3 bucket (optional, for cloud storage)

## Local Setup

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file based on `.env.example`:
   ```
   POSTGRES_URI="postgresql+psycopg2://username:password@hostname:port/database"
   POSTGRES_USER="username"
   POSTGRES_PASSWORD="password"
   POSTGRES_HOST="hostname"
   POSTGRES_PORT="5432"
   POSTGRES_DB="database_name"
   INIT_DB="false"  # Set to "true" to initialize the database with sample data

   # AWS S3 Configuration (optional)
   AWS_ACCESS_KEY_ID="your_access_key_id"
   AWS_SECRET_ACCESS_KEY="your_secret_access_key"
   AWS_REGION="us-east-1"
   S3_BUCKET_NAME="your-s3-bucket-name"
   USE_S3_STORAGE="true"  # Set to "false" to use local storage instead of S3
   ```
4. Run the application:
   ```
   streamlit run 1_Dashboard.py
   ```

## Docker Deployment

This project includes Docker support for easy deployment. See [DOCKER.md](DOCKER.md) for detailed instructions.

Quick start:
```bash
# Build and run with Docker Compose
docker-compose up --build

# Or use the test script
./build_and_test.sh
```

## AWS App Runner Deployment

This project is configured for deployment to AWS App Runner. See [AWS_DEPLOYMENT.md](AWS_DEPLOYMENT.md) for detailed instructions.

Key files:
- `apprunner.yaml`: Configuration for AWS App Runner
- `Dockerfile`: Container definition

## AWS Deployment

### Option 1: EC2 Deployment with Docker

1. Launch an EC2 instance with sufficient resources (recommended: t3.large or better)
2. Install Docker and Docker Compose on the instance
3. Clone the repository to the instance
4. Create a `.env` file with your PostgreSQL credentials and AWS S3 settings
5. Build and start the containers:
   ```
   docker-compose up -d
   ```
6. Configure security groups to allow traffic on port 8501

### Option 2: AWS Elastic Beanstalk Deployment

1. Install the AWS CLI and EB CLI
2. Initialize an Elastic Beanstalk application:
   ```
   eb init -p docker
   ```
3. Create the environment:
   ```
   eb create llm-benchmark-env
   ```
4. Set environment variables for database credentials and S3 settings:
   ```
   eb setenv POSTGRES_USER=username POSTGRES_PASSWORD=password POSTGRES_HOST=hostname POSTGRES_PORT=5432 POSTGRES_DB=database_name AWS_ACCESS_KEY_ID=your_access_key AWS_SECRET_ACCESS_KEY=your_secret_key AWS_REGION=us-east-1 S3_BUCKET_NAME=your-bucket-name USE_S3_STORAGE=true
   ```
5. Deploy the application:
   ```
   eb deploy
   ```

### Option 3: AWS ECS Deployment

1. Create an ECR repository for the application
2. Build and push the Docker image to ECR
3. Create an ECS cluster
4. Define a task definition with the container image and environment variables
5. Create a service to run the task
6. Configure an Application Load Balancer to route traffic to the service

## Data Structure

The application expects benchmark data in the following structure:

```
data/
  ├── RTX4090/
  │   ├── llama-2-7b-chat-q4_K_M/
  │   │   └── log.txt
  │   ├── llama3-8b-instruct-q2_K/
  │   │   └── log.txt
  │   ├── llama3-latest/
  │   │   └── log.txt
  │   ├── llama2:7b-chat-q4_K_M.txt
  │   ├── llama2:7b-chat-q4_K_M-short.csv
  │   ├── llama2:7b-chat-q4_K_M-long.csv
  │   └── ...
  ├── RTX4080S/
  │   └── ...
  └── ADA6000-Latest/
      └── ...
```

When using S3 storage, the same structure is expected in your S3 bucket.

## S3 Integration

The application can store and read logs and benchmark data from Amazon S3:

1. Create an S3 bucket to store your data
2. Configure AWS credentials in your `.env` file:
   ```
   AWS_ACCESS_KEY_ID=your_access_key_id
   AWS_SECRET_ACCESS_KEY=your_secret_access_key
   AWS_REGION=us-east-1
   S3_BUCKET_NAME=your-s3-bucket-name
   USE_S3_STORAGE=true
   ```
3. When uploading logs through the Chat Audit page, they will be stored in both local storage and S3
4. The application will automatically check for files in S3 before falling back to local storage
5. The Chat Viewer page will display logs from both S3 and local storage

### S3 Data Organization

The application organizes data in S3 as follows:

- `logs/` - Contains uploaded chat logs
- `benchmarks/` - Contains benchmark data with the same structure as the local `data/` directory

## Database Setup

The application uses PostgreSQL for storing audit data. The schema will be automatically created when the application starts.

### Custom GPU and Model Names

The application now supports adding custom GPU and model names:

1. In the Chat Audit page, you can add custom GPU and model names by checking the "Add Custom" checkbox
2. Enter the name of your custom GPU or model and click "Add"
3. The custom entry will be saved to the database and available for selection
4. In the Audit History page, custom entries are marked with a "Custom" tag
5. You can filter to show only custom entries using the "Show Custom Entries Only" checkbox

## Troubleshooting

- **Missing data directories**: The application will create missing directories but you need to populate them with benchmark data
- **Database connection issues**: Check your PostgreSQL credentials and ensure the database is accessible from the application
- **File not found errors**: Ensure your data files follow the expected naming convention and directory structure
- **S3 access issues**: Verify your AWS credentials and bucket permissions; the application will fall back to local storage if S3 is unavailable

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 