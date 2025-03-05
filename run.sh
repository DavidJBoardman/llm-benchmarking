#!/bin/bash
# Run script for LLM Benchmark Dashboard

# Initialize database with sample data (optional)
if [ "$1" == "--init-db" ]; then
    echo "Initializing database with sample data..."
    python init_sample_data.py
fi

# Run the Streamlit application
echo "Starting LLM Benchmark Dashboard..."
streamlit run 1_Dashboard.py 