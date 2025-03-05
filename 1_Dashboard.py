import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import json
import os
import logging
from utils.db import init_db
from utils.file_storage import read_file, read_csv, is_using_s3, get_file_path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize database tables
init_db()

# Define data directory
DATA_DIR = "data"

# Ensure data directory exists
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
    logger.warning(f"Created missing data directory: {DATA_DIR}")

st.set_page_config(layout="wide", page_title="LLM Benchmark Dashboard")

# Function to read performance metrics from txt files
def read_performance_metrics(file_path):
    try:
        content = read_file(file_path)
        if content is None:
            logger.warning(f"File not found: {file_path}")
            return {}
        
        lines = content.splitlines()
        metrics = {}
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                metrics[key.strip()] = value.strip()
        return metrics
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {str(e)}")
        st.error(f"Error reading file {file_path}: {str(e)}")
        return {}

# Function to read and process CSV files
def read_benchmark_csv(file_path):
    try:
        df = read_csv(file_path)
        if df is None:
            logger.warning(f"CSV file not found: {file_path}")
            return pd.DataFrame()
        
        # Fix timestamp format by adding space between date and time
        df['timestamp'] = df['timestamp'].str.replace(r'(\d{4}/\d{2}/\d{2})(\d{2}:\d{2}:\d{2}\.\d+)', r'\1 \2', regex=True)
        df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y/%m/%d %H:%M:%S.%f')
        
        # Convert to relative time in seconds from start
        start_time = df['timestamp'].min()
        df['relative_time'] = (df['timestamp'] - start_time).dt.total_seconds()
        return df
    except Exception as e:
        logger.error(f"Error processing CSV file {file_path}: {str(e)}")
        st.error(f"Error processing CSV file {file_path}: {str(e)}")
        return pd.DataFrame()

# Style and layout
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stPlotlyChart {
        background-color: #ffffff;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .info-box {
        background-color: #2a4365;
        color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border-left: 4px solid #4299e1;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🚀 LLM Benchmark Dashboard")

# Display S3 status
if is_using_s3():
    st.markdown(
        """<div class="info-box">
            📥 S3 storage is enabled. Benchmark data will be read from S3 if available.
        </div>""",
        unsafe_allow_html=True
    )

# Define all benchmark files for both GPUs
gpu_model_files = {
    "RTX 4090": {
        "directory": "RTX4090",
        "models": {
            "llama2-7b-chat": {
                "txt": "llama2:7b-chat-q4_K_M.txt",
                "short": "llama2:7b-chat-q4_K_M-short.csv",
                "long": "llama2:7b-chat-q4_K_M-long.csv",
                "very_long": "llama2:7b-chat-q4_K_M-very-long.csv"
            },
            "llama3-8b-instruct": {
                "txt": "llama3:8b-instruct-q2_K.txt",
                "short": "llama3:8b-instruct-q2_K-short.csv",
                "long": "llama3:8b-instruct-q2_K-long.csv",
                "very_long": "llama3:8b-instruct-q2_K-very-long.csv"
            },
            "llama3-latest": {
                "txt": "llama3:latest.txt",
                "short": "llama3:latest-short.csv",
                "long": "llama3:latest-long.csv",
                "very_long": "llama3:latest-very-long.csv"
            }
        }
    },
    "RTX 4080S": {
        "directory": "RTX4080S",
        "models": {
            "llama2-7b-chat": {
                "txt": "llama2:7b-chat-q4_K_M.txt",
                "short": "llama2:7b-chat-q4_K_M-short.csv",
                "long": "llama2:7b-chat-q4_K_M-long.csv",
                "very_long": "llama2:7b-chat-q4_K_M-very-long.csv"
            },
            "llama3-8b-instruct": {
                "txt": "llama3:8b-instruct-q2_K.txt",
                "short": "llama3:8b-instruct-q2_K-short.csv",
                "long": "llama3:8b-instruct-q2_K-long.csv",
                "very_long": "llama3:8b-instruct-q2_K-very-long.csv"
            },
            "llama3-latest": {
                "txt": "llama3:latest.txt",
                "short": "llama3:latest-short.csv",
                "long": "llama3:latest-long.csv",
                "very_long": "llama3:latest-very-long.csv"
            }
        }
    },
    "ADA 6000": {
        "directory": "ADA6000-Latest",
        "models": {
            "llama2-7b-chat": {
                "txt": "llama2-7b-chat-q4_K_M.txt",
                "short": "llama2-7b-chat-q4_K_M-short.csv",
                "long": "llama2-7b-chat-q4_K_M-long.csv",
                "very_long": "llama2-7b-chat-q4_K_M-very-long.csv"
            },
            "llama3-8b-instruct": {
                "txt": "llama3-8b-instruct-q2_K.txt",
                "short": "llama3-8b-instruct-q2_K-short.csv",
                "long": "llama3-8b-instruct-q2_K-long.csv",
                "very_long": "llama3-8b-instruct-q2_K-very-long.csv"
            },
            "llama3-latest": {
                "txt": "llama3-latest.txt",
                "short": "llama3-latest-short.csv",
                "long": "llama3-latest-long.csv",
                "very_long": "llama3-latest-very-long.csv"
            }
        }
    }
}

# Helper function to get file path (local or S3)
def get_benchmark_file_path(gpu, model, file_type):
    """Get the file path for a benchmark file, checking S3 first if enabled."""
    # Try S3 path first
    s3_path = f"benchmarks/{gpu_model_files[gpu]['directory']}/{gpu_model_files[gpu]['models'][model][file_type]}"
    file_path = get_file_path(s3_path, "", check_s3=True)
    
    # If not found in S3, use local path
    if not file_path.startswith("s3://"):
        file_path = os.path.join(DATA_DIR, f"{gpu_model_files[gpu]['directory']}/{gpu_model_files[gpu]['models'][model][file_type]}")
    
    return file_path

# Check if data directories exist
available_gpus = []
for gpu in gpu_model_files:
    gpu_dir = os.path.join(DATA_DIR, gpu_model_files[gpu]['directory'])
    if os.path.exists(gpu_dir):
        available_gpus.append(gpu)
    else:
        logger.warning(f"GPU directory not found: {gpu_dir}")

if not available_gpus:
    st.warning(f"No GPU data directories found in {DATA_DIR}. Please ensure data is properly loaded.")

# Sidebar for selection
st.sidebar.title("Settings")

# GPU Selection
selected_gpus = st.sidebar.multiselect(
    "Select GPUs to Compare",
    available_gpus,
    default=available_gpus
)

# Model Selection
if selected_gpus:
    all_models = list(gpu_model_files[selected_gpus[0]]["models"].keys())
    selected_models = st.sidebar.multiselect(
        "Select Models to Compare",
        all_models,
        default=all_models
    )
else:
    all_models = []
    selected_models = []
    st.sidebar.warning("No GPUs available for selection")

run_type = st.sidebar.selectbox(
    "Select Run Type",
    ["short", "long", "very_long"]
)

# After the run_type selection in sidebar, add:
comparison_mode = st.sidebar.radio(
    "Comparison Mode",
    ["Absolute Values", "Relative (%)"]
)

# Performance Metrics Comparison
st.header("⚡ Performance Metrics Comparison")

# Collect metrics for all selected GPUs and models
metrics_data = {}
for gpu in selected_gpus:
    for model in selected_models:
        model_key = f"{gpu} - {model}"
        try:
            file_path = get_benchmark_file_path(gpu, model, "txt")
            metrics = read_performance_metrics(file_path)
            if metrics:
                metrics_data[model_key] = metrics
        except Exception as e:
            logger.warning(f"Could not read metrics for {model_key}: {str(e)}")
            st.warning(f"Could not read metrics for {model_key}: {str(e)}")

if metrics_data:
    # Clean and process metrics for visualization
    def clean_metric_value(value):
        if isinstance(value, str):
            # Remove units and convert to float
            try:
                return float(''.join(c for c in value.split()[0] if c.isdigit() or c == '.'))
            except ValueError:
                return 0
        return value

    # Process metrics for visualization
    viz_metrics = {}
    for model_key in metrics_data:
        viz_metrics[model_key] = {
            'Token Generation Speed (tokens/s)': clean_metric_value(metrics_data[model_key].get('eval rate', '0')),
            'Total Duration (s)': clean_metric_value(metrics_data[model_key].get('total duration', '0')),
            'Load Duration (ms)': clean_metric_value(metrics_data[model_key].get('load duration', '0')),
            'Prompt Eval Duration (ms)': clean_metric_value(metrics_data[model_key].get('prompt eval duration', '0')),
            'Prompt Eval Rate (tokens/s)': clean_metric_value(metrics_data[model_key].get('prompt eval rate', '0')),
            'Prompt Token Count': clean_metric_value(metrics_data[model_key].get('prompt eval count', '0')),
            'Generation Token Count': clean_metric_value(metrics_data[model_key].get('eval count', '0')),
        }
    
    viz_df = pd.DataFrame(viz_metrics).T
    
    # Display summary table
    st.subheader("📊 Performance Summary Table")
    st.markdown("_Green highlights indicate best values, orange highlights indicate areas for improvement_")
    
    st.dataframe(
        viz_df.style.highlight_max(axis=0, color='#a8e6cf')
                .highlight_min(axis=0, color='#ffd3b6'),
        height=300
    )
    
    # Create metric comparisons in a grid
    st.subheader("📈 Detailed Metric Comparisons")
    
    metrics_to_compare = [
        ('Token Generation Speed (tokens/s)', 'Higher is better - Main generation performance metric'),
        ('Total Duration (s)', 'Lower is better - Overall execution time'),
        ('Load Duration (ms)', 'Lower is better - Model initialization time'),
        ('Prompt Eval Rate (tokens/s)', 'Higher is better - Initial response speed'),
        ('Generation Token Count', 'Output size reference'),
        ('Prompt Token Count', 'Input size reference')
    ]
    
    for i in range(0, len(metrics_to_compare), 2):
        col1, col2 = st.columns(2)
        
        # First metric in the row
        metric, note = metrics_to_compare[i]
        with col1:
            st.markdown(f"**{metric}**\n_{note}_")
            fig = go.Figure()
            
            if comparison_mode == "Absolute Values":
                for model_key in viz_metrics:
                    fig.add_trace(go.Bar(
                        name=model_key,
                        x=[model_key],
                        y=[viz_metrics[model_key][metric]],
                        text=[f"{viz_metrics[model_key][metric]:.2f}"],
                        textposition='auto',
                    ))
                fig.update_layout(
                    showlegend=False,
                    height=300,
                    yaxis_title=metric,
                    xaxis_tickangle=45
                )
            else:
                # Calculate relative values
                max_val = max([viz_metrics[m][metric] for m in viz_metrics])
                min_val = min([viz_metrics[m][metric] for m in viz_metrics])
                baseline = min_val if "better" in note.lower() else max_val
                
                for model_key in viz_metrics:
                    value = viz_metrics[model_key][metric]
                    if baseline != 0:
                        relative_val = ((value / baseline) - 1) * 100
                        # Invert percentage for metrics where lower is better
                        if "lower" in note.lower():
                            relative_val = -relative_val
                        
                        fig.add_trace(go.Bar(
                            name=model_key,
                            x=[model_key],
                            y=[relative_val],
                            text=[f"{relative_val:+.1f}%"],
                            textposition='auto',
                        ))
                
                fig.update_layout(
                    showlegend=False,
                    height=300,
                    yaxis_title="% Difference from Baseline",
                    xaxis_tickangle=45
                )
                fig.add_hline(y=0, line_dash="dash", line_color="gray")
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Second metric in the row (if available)
        if i + 1 < len(metrics_to_compare):
            metric, note = metrics_to_compare[i + 1]
            with col2:
                st.markdown(f"**{metric}**\n_{note}_")
                fig = go.Figure()
                
                if comparison_mode == "Absolute Values":
                    for model_key in viz_metrics:
                        fig.add_trace(go.Bar(
                            name=model_key,
                            x=[model_key],
                            y=[viz_metrics[model_key][metric]],
                            text=[f"{viz_metrics[model_key][metric]:.2f}"],
                            textposition='auto',
                        ))
                    fig.update_layout(
                        showlegend=False,
                        height=300,
                        yaxis_title=metric,
                        xaxis_tickangle=45
                    )
                else:
                    # Calculate relative values
                    max_val = max([viz_metrics[m][metric] for m in viz_metrics])
                    min_val = min([viz_metrics[m][metric] for m in viz_metrics])
                    baseline = min_val if "better" in note.lower() else max_val
                    
                    for model_key in viz_metrics:
                        value = viz_metrics[model_key][metric]
                        if baseline != 0:
                            relative_val = ((value / baseline) - 1) * 100
                            # Invert percentage for metrics where lower is better
                            if "lower" in note.lower():
                                relative_val = -relative_val
                            
                            fig.add_trace(go.Bar(
                                name=model_key,
                                x=[model_key],
                                y=[relative_val],
                                text=[f"{relative_val:+.1f}%"],
                                textposition='auto',
                            ))
                    
                    fig.update_layout(
                        showlegend=False,
                        height=300,
                        yaxis_title="% Difference from Baseline",
                        xaxis_tickangle=45
                    )
                    fig.add_hline(y=0, line_dash="dash", line_color="gray")
                
                st.plotly_chart(fig, use_container_width=True)

    # Add a model recommendation section
    st.header("🏆 Performance Analysis")
    
    fastest_model = viz_df['Token Generation Speed (tokens/s)'].idxmax()
    lowest_latency = viz_df['Total Duration (s)'].idxmin()
    fastest_prompt = viz_df['Prompt Eval Rate (tokens/s)'].idxmax()
    
    st.markdown(f"""
    ### Key Findings:
    - **Fastest Generation**: {fastest_model} ({viz_df.loc[fastest_model, 'Token Generation Speed (tokens/s)']:.2f} tokens/s)
    - **Lowest Latency**: {lowest_latency} ({viz_df.loc[lowest_latency, 'Total Duration (s)']:.2f} seconds)
    - **Fastest Prompt Processing**: {fastest_prompt} ({viz_df.loc[fastest_prompt, 'Prompt Eval Rate (tokens/s)']:.2f} tokens/s)
    """)
else:
    st.warning("No performance metrics data available for the selected GPUs and models.")

# GPU Metrics Over Time
st.header("📈 GPU Resource Usage Over Time")

metrics_to_plot = st.multiselect(
    "Select Metrics to Plot",
    [
        ("GPU Temperature (°C)", "gpu_temp"),
        ("GPU Utilization (%)", "utilization_gpu"),
        ("Memory Utilization (%)", "utilization_mem"),
        ("Power Draw (W)", "power_draw")
    ],
    default=[("GPU Utilization (%)", "utilization_gpu"), ("Power Draw (W)", "power_draw")],
    format_func=lambda x: x[0]
)

# Load and plot CSV data
for metric_label, metric in metrics_to_plot:
    st.subheader(metric_label)
    fig = go.Figure()
    
    data_available = False
    for gpu in selected_gpus:
        for model in selected_models:
            try:
                file_path = get_benchmark_file_path(gpu, model, run_type)
                df = read_benchmark_csv(file_path)
                if not df.empty and metric in df.columns:
                    fig.add_trace(go.Scatter(
                        x=df['relative_time'],
                        y=df[metric],
                        name=f"{gpu} - {model}",
                        mode='lines'
                    ))
                    data_available = True
            except Exception as e:
                logger.warning(f"Could not read data for {gpu} - {model}: {str(e)}")
    
    if data_available:
        fig.update_layout(
            xaxis_title="Time (seconds)",
            yaxis_title=metric_label,
            height=400,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=1.02,  # Position legend outside the plot area
                bordercolor="rgba(0, 0, 0, 0.2)",    # Light border
                borderwidth=1
            ),
            margin=dict(r=150)  # Add right margin to accommodate legend
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info(f"No data available for {metric_label} with the current selection.")

# Footer
st.markdown("---")
st.markdown("📊 Dashboard created for comparing LLM benchmark performance across different GPUs") 