#!/bin/bash

# Setup script for LLM Benchmarking Tool

# Create virtual environment
echo "Creating virtual environment..."
python -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create data directory structure
echo "Creating data directory structure..."
mkdir -p data/RTX4090 data/RTX4080S data/ADA6000 data/ADA6000-Latest

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Please update the .env file with your database credentials."
fi

echo "Setup complete! You can now run the benchmark tool."
echo "To run the dashboard: streamlit run 1_Dashboard.py" 