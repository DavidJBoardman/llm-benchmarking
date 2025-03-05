#!/bin/bash

# Build the Docker image
echo "Building Docker image..."
docker build -t llm-benchmarking-dashboard .

# Check if the build was successful
if [ $? -ne 0 ]; then
    echo "Error: Docker build failed."
    exit 1
fi

echo "Docker image built successfully."

# Run the Docker container
echo "Running Docker container for testing..."
docker run -p 8080:8080 --env-file .env --name llm-benchmarking-test -d llm-benchmarking-dashboard

# Check if the container started successfully
if [ $? -ne 0 ]; then
    echo "Error: Failed to start Docker container."
    exit 1
fi

echo "Docker container started. Waiting for application to initialize..."
sleep 10

# Check if the application is healthy
echo "Checking application health..."
if curl -s -f http://localhost:8080/_stcore/health > /dev/null; then
    echo "Application is healthy and running at http://localhost:8080"
    echo "Press Ctrl+C to stop the container when done testing."
    
    # Wait for user to press Ctrl+C
    trap "docker stop llm-benchmarking-test && docker rm llm-benchmarking-test" INT
    echo "Container logs:"
    docker logs -f llm-benchmarking-test
else
    echo "Error: Application health check failed."
    echo "Container logs:"
    docker logs llm-benchmarking-test
    
    # Clean up
    docker stop llm-benchmarking-test
    docker rm llm-benchmarking-test
    exit 1
fi 