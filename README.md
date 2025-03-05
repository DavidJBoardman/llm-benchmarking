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

## Database Schema

The application uses the following database tables:

- `chat_audits` - Stores audit records of LLM interactions
- `gpu_models` - Stores available GPU models
- `llm_models` - Stores available LLM models

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 