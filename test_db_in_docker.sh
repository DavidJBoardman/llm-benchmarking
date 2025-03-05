#!/bin/bash

# Load environment variables from .env file
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
  echo "Loaded environment variables from .env file"
else
  echo "Error: .env file not found"
  exit 1
fi

# Print database connection details
echo "Database Host: $POSTGRES_HOST"
echo "Database Port: $POSTGRES_PORT"
echo "Database Name: $POSTGRES_DB"
echo "Database User: $POSTGRES_USER"

# Build the Docker image
echo "Building Docker image..."
docker build -t benchmarks-app .

# Run the container with the test script
echo "Running database connection test in Docker container..."
docker run --rm \
  --network host \
  -e POSTGRES_URI="postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@$POSTGRES_HOST:$POSTGRES_PORT/$POSTGRES_DB" \
  -e POSTGRES_USER="$POSTGRES_USER" \
  -e POSTGRES_PASSWORD="$POSTGRES_PASSWORD" \
  -e POSTGRES_HOST="$POSTGRES_HOST" \
  -e POSTGRES_PORT="$POSTGRES_PORT" \
  -e POSTGRES_DB="$POSTGRES_DB" \
  -v $(pwd)/test_db_connection.py:/app/test_db_connection.py \
  benchmarks-app \
  python test_db_connection.py 