#!/bin/bash

# This script tests the application locally before deploying to AWS App Runner

# Load environment variables from .env file
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
  echo "Loaded environment variables from .env file"
else
  echo "Error: .env file not found"
  exit 1
fi

# Stop any running containers
echo "Stopping any running containers..."
docker-compose down

# Build and start the application
echo "Building and starting the application..."
docker-compose up --build -d

# Wait for the application to start
echo "Waiting for the application to start..."
sleep 10

# Check if the application is healthy
echo "Checking if the application is healthy..."
HEALTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/_stcore/health)

if [ "$HEALTH_STATUS" == "200" ]; then
  echo "Application is healthy!"
  echo "You can access the application at: http://localhost:8080"
  
  # Test database connection
  echo "Testing database connection..."
  docker exec benchmarks-app-1 python -c "
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Get database credentials from environment variables
DB_USER = os.getenv('POSTGRES_USER')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD')
DB_HOST = os.getenv('POSTGRES_HOST')
DB_PORT = os.getenv('POSTGRES_PORT', '5432')
DB_NAME = os.getenv('POSTGRES_DB')

# Create database URL
POSTGRES_URI = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

print(f'Attempting to connect to database at: {DB_HOST}:{DB_PORT}')
print(f'Database name: {DB_NAME}')
print(f'Database user: {DB_USER}')

# Try to connect
engine = create_engine(POSTGRES_URI)
with engine.connect() as conn:
    result = conn.execute(text('SELECT 1'))
    print('Database connection successful!')
    
    # Get database version
    version = conn.execute(text('SELECT version()'))
    print('Database version:', version.fetchone()[0])
    
    # List tables
    tables = conn.execute(text(\"\"\"
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema='public'
    \"\"\"))
    print('Tables in database:')
    for table in tables:
        print(f'  - {table[0]}')
"
  
  echo ""
  echo "All tests passed! The application is ready to be deployed to AWS App Runner."
  echo "To deploy, follow the instructions in AWS_DEPLOYMENT.md"
else
  echo "Error: Application is not healthy. Status code: $HEALTH_STATUS"
  echo "Check the logs for more information:"
  docker-compose logs
  exit 1
fi 