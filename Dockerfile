# Use a slim base image for smaller size
FROM --platform=linux/amd64 python:3.11-slim

WORKDIR /app

# Install only necessary system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create necessary directories with correct permissions
RUN mkdir -p data logs && chmod -R 777 data logs

# Create Streamlit config directory and configuration
RUN mkdir -p /root/.streamlit
RUN echo "\
[server]\n\
enableCORS = false\n\
enableXsrfProtection = false\n\
enableWebsocketCompression = false\n\
headless = true\n\
" > /root/.streamlit/config.toml

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8501

# Expose the port Streamlit runs on
EXPOSE 8501

# Health check for AWS App Runner
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Command to run the application
CMD ["streamlit", "run", "1_Dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
