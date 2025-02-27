#!/bin/bash

# Create data directory if it doesn't exist
DATA_DIR="data"
mkdir -p "$DATA_DIR"

# List available language models
echo "Fetching available language models..."
ollama list

# Prompt user to choose a model
read -p "Enter the name of the language model you want to use: " model_name

# Ensure a model name is provided
if [ -z "$model_name" ]; then
    echo "Model name cannot be empty. Exiting."
    exit 1
fi

# Get GPU information
gpu_name=$(nvidia-smi --query-gpu=name --format=csv,noheader | head -n 1 | tr -d ' ' | tr -d ',')
echo "Detected GPU: $gpu_name"

# Create directory for this GPU if it doesn't exist
GPU_DIR="$DATA_DIR/$gpu_name"
mkdir -p "$GPU_DIR"

# Set filename to model name with .csv extension
filename="$GPU_DIR/${model_name}-short.csv"

# Write headers to CSV
echo "timestamp,gpu_index,gpu_name,gpu_temp,utilization_gpu,utilization_mem,gpu_mem_total,gpu_mem_used,gpu_mem_free,fan_speed,power_draw,clocks_sm,clocks_mem,clocks_gr,clocks_video,compute_mode,cpu_usage,ram_total,ram_used,ram_free,disk_total,disk_used,disk_free" > "$filename"

# Function to log system metrics
log_metrics() {
    gpu_data=$(nvidia-smi --query-gpu=timestamp,index,name,temperature.gpu,utilization.gpu,utilization.memory,memory.total,memory.used,memory.free,fan.speed,power.draw,clocks.sm,clocks.mem,clocks.gr,clocks.video,compute_mode --format=csv,noheader,nounits | tr -d ' ')

    cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2 + $4}') # user + sys usage

    read ram_total ram_used ram_free <<<$(free -m | awk 'NR==2{print $2, $3, $4}')

    read disk_total disk_used disk_free <<<$(df -h / | awk 'NR==2 {print $2, $3, $4}')

    echo "$gpu_data,$cpu_usage,$ram_total,$ram_used,$ram_free,$disk_total,$disk_used,$disk_free" >> "$filename"
}

# Start logging metrics in the background
echo "Starting system monitoring... Logging to '$filename'"
while true; do 
    log_metrics
    sleep 0.2  # Adjust if needed
done &  # Run in background

# Run the selected language model
echo "Starting model '$model_name'..."
ollama run "$model_name" &  # Run in background
OLLAMA_PID=$!  # Store the process ID

# Wait for the model to load
sleep 5

# Send input to the model
echo "Tell me a story." | ollama run "$model_name"

# Stop logging when the model process ends
wait $OLLAMA_PID
echo "Model execution finished. Stopping logging."

sleep 5

# Kill the background logging process
pkill -P $$

echo "Metrics logging complete. Data saved to '$filename'."

