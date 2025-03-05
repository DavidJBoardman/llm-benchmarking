import streamlit as st
import pandas as pd
from pathlib import Path
import re
import os
from utils.file_storage import read_file, list_files, is_using_s3

# Define data directory
DATA_DIR = "data"

st.set_page_config(layout="wide", page_title="LLM Chat Logs Viewer")

# Style and layout
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .chat-message {
        padding: 1.5rem;
        margin: 0.5rem 0;
        border-radius: 0.5rem;
        line-height: 1.5;
        position: relative;
    }
    .user-message {
        background-color: #2d3748;
        border-left: 4px solid #4a5568;
        color: #ffffff;
    }
    .assistant-message {
        background-color: #1a365d;
        border-left: 4px solid #2b6cb0;
        color: #ffffff;
    }
    .error-message {
        background-color: #742a2a;
        border-left: 4px solid #9b2c2c;
        color: #ffffff;
    }
    .chat-message strong {
        color: #63b3ed;
        font-size: 1.1em;
        display: block;
        margin-bottom: 0.5rem;
    }
    .chat-message code {
        background-color: #4a5568;
        padding: 0.2em 0.4em;
        border-radius: 0.3em;
        font-size: 0.9em;
    }
    .metrics-text {
        color: #a0aec0;
        margin-top: 0.5rem;
        text-align: right;
        font-size: 0.85em;
    }

    div[data-testid="stHorizontalBlock"] {
        gap: 0.2rem !important;
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

st.title("💬 LLM Chat Logs Viewer")

# Check if S3 is available
if is_using_s3():
    st.markdown(
        """<div class="info-box">
            📥 S3 storage is enabled. Logs will be read from S3 when available.
        </div>""",
        unsafe_allow_html=True
    )

# Define the model folders and their log files
chat_logs = {
    "RTX 4090": {
        "llama3-latest": os.path.join(DATA_DIR, "RTX4090", "llama3-latest", "log.txt"),
        "llama3-8b-instruct": os.path.join(DATA_DIR, "RTX4090", "llama3-8b-instruct-q2_K", "log.txt"),
        "llama2-7b-chat": os.path.join(DATA_DIR, "RTX4090", "llama-2-7b-chat-q4_K_M", "log.txt")
    },
    "RTX 4080S": {
        "llama3-latest": os.path.join(DATA_DIR, "RTX4080S", "llama3-latest", "log.txt"),
        "llama3-8b-instruct": os.path.join(DATA_DIR, "RTX4080S", "llama3-8b-instruct-q2_K", "log.txt"),
        "llama2-7b-chat": os.path.join(DATA_DIR, "RTX4080S", "llama-2-7b-chat-q4_K_M", "log.txt")
    },
    "ADA 6000": {
        "llama3-latest": os.path.join(DATA_DIR, "ADA6000-Latest", "llama3-latest", "log.txt"),
        "llama3-8b-instruct": os.path.join(DATA_DIR, "ADA6000-Latest", "llama3-8b-instruct-q2_K", "log.txt"),
        "llama2-7b-chat": os.path.join(DATA_DIR, "ADA6000-Latest", "llama-2-7b-chat-q4_K_M", "log.txt")
    }
}

def read_chat_log(file_path):
    """Read a chat log file from storage."""
    content = read_file(file_path)
    if content is None:
        return f"Error: Log file not found: {file_path}"
    return content

def parse_chat_log(content):
    # Split the log into individual messages
    messages = []
    current_message = None
    
    # Regular expressions for parsing
    user_query_pattern = r'\[DEBUG\]\[User \| .*?\]: querying model with prompt: (.*?)(?=cpu usage)'
    system_metrics_pattern = r'cpu usage: (.*?)%\ngpu usage: (.*?)%\nram usage: (.*?)%\nvram usage: (.*?)%'
    response_pattern = r'\[DEBUG\]\[User \| .*?\]: unformated response: (.*?)(?=cpu usage|\[INFO\]|$)'
    
    # Find all user queries with their timestamps
    user_queries = re.finditer(user_query_pattern, content, re.DOTALL)
    responses = re.finditer(response_pattern, content, re.DOTALL)
    
    # Combine queries and responses
    conversation = []
    
    for query in user_queries:
        # Get the user message
        user_text = query.group(1).strip()
        # Get system metrics after the query
        metrics_match = re.search(system_metrics_pattern, content[query.end():])
        if metrics_match:
            metrics = {
                'cpu': float(metrics_match.group(1)),
                'gpu': float(metrics_match.group(2)),
                'ram': float(metrics_match.group(3)),
                'vram': float(metrics_match.group(4))
            }
        else:
            metrics = None
            
        conversation.append({
            'role': 'user',
            'content': user_text,
            'metrics': metrics
        })
    
    # Add responses
    for response in responses:
        response_text = response.group(1).strip()
        # Get system metrics after the response
        metrics_match = re.search(system_metrics_pattern, content[response.end():])
        if metrics_match:
            metrics = {
                'cpu': float(metrics_match.group(1)),
                'gpu': float(metrics_match.group(2)),
                'ram': float(metrics_match.group(3)),
                'vram': float(metrics_match.group(4))
            }
        else:
            metrics = None
            
        conversation.append({
            'role': 'assistant',
            'content': response_text,
            'metrics': metrics
        })
    
    # Sort conversation by the order in the log
    conversation.sort(key=lambda x: content.index(x['content']))
    
    return conversation

# Helper function to display chat messages
def display_chat_messages(messages):
    for msg in messages:
        message_content = msg['content']
        metrics_html = ""
        
        if msg.get('metrics'):
            metrics_html = f"""<div class="metrics-text">
                CPU: {msg['metrics']['cpu']}% • GPU: {msg['metrics']['gpu']}% • RAM: {msg['metrics']['ram']}% • VRAM: {msg['metrics']['vram']:.2f}%
            </div>"""
        
        if msg['role'] == "user":
            st.markdown(
                f"""<div class="chat-message user-message">
                    <strong>User:</strong>
                    {message_content}
                    {metrics_html}
                    </div>
                    """,
                unsafe_allow_html=True
            )
        elif msg['role'] == "assistant":
            st.markdown(
                f"""<div class="chat-message assistant-message">
                    <strong>Assistant:</strong>
                    {message_content}
                    {metrics_html}
                    </div>
                    """,
                unsafe_allow_html=True
            )

# Get S3 logs if available
s3_logs = {}
if is_using_s3():
    s3_log_files = list_files(prefix="logs/")
    if s3_log_files:
        s3_logs["S3 Uploaded Logs"] = {}
        
        # Process each S3 log file
        for log_file in s3_log_files:
            if log_file.startswith("s3://"):
                filename = log_file.split('/')[-1]
                
                # Try to extract model and GPU info from filename
                # Format: model_gpu_timestamp_uniqueid.txt
                parts = filename.split('_')
                if len(parts) >= 4:  # At least model, gpu, timestamp, and some part of uniqueid
                    # Extract model and GPU from filename
                    model_name = parts[0]
                    gpu_name = parts[1]
                    timestamp = parts[2]
                    
                    # Format the display name
                    display_name = f"{model_name} on {gpu_name} ({timestamp})"
                else:
                    # If filename doesn't match expected format, use the original filename
                    display_name = filename
                
                s3_logs["S3 Uploaded Logs"][display_name] = log_file

# Combine local and S3 logs
all_logs = {**chat_logs, **s3_logs}

# Sidebar for GPU and model selection
st.sidebar.title("Settings")

# Add layout toggle
layout_mode = st.sidebar.radio(
    "Layout Mode",
    ["Side by Side", "Tabs"],
    help="Choose how to display the chat comparisons"
)

selected_gpus = st.sidebar.multiselect(
    "Select GPUs to Compare",
    list(all_logs.keys()),
    default=[list(all_logs.keys())[0]]
)

# Get all unique models across selected GPUs
all_models = set()
for gpu in selected_gpus:
    all_models.update(all_logs[gpu].keys())

selected_models = st.sidebar.multiselect(
    "Select Models to View",
    list(all_models),
    default=[list(all_models)[0]] if all_models else []
)

# Main content area
if selected_gpus and selected_models:
    if layout_mode == "Side by Side":
        for model in selected_models:
            st.subheader(f"Model: {model}")
            
            # Create columns for each GPU that has this model
            gpu_cols = st.columns(len(selected_gpus))
            
            for gpu, col in zip(selected_gpus, gpu_cols):
                if model in all_logs[gpu]:
                    with col:
                        st.markdown(f"##### {gpu}")
                        log_content = read_chat_log(all_logs[gpu][model])
                        if log_content.startswith("Error"):
                            st.error(log_content)
                            continue
                        
                        messages = parse_chat_log(log_content)
                        
                        # Chat Statistics at the top
                        user_messages = len([m for m in messages if m['role'] == "user"])
                        assistant_messages = len([m for m in messages if m['role'] == "assistant"])
                        
                        stat_cols = st.columns(4)
                        with stat_cols[0]:
                            st.metric("Total", len(messages))
                        with stat_cols[1]:
                            st.metric("User", user_messages)
                        with stat_cols[2]:
                            st.metric("Assistant", assistant_messages)
                        
                        # Average Resource Usage
                        if any(m.get('metrics') for m in messages):
                            metrics = [m['metrics'] for m in messages if m.get('metrics')]
                            avg_cpu = sum(m['cpu'] for m in metrics) / len(metrics)
                            avg_gpu = sum(m['gpu'] for m in metrics) / len(metrics)
                            avg_ram = sum(m['ram'] for m in metrics) / len(metrics)
                            avg_vram = sum(m['vram'] for m in metrics) / len(metrics)
                            
                            st.markdown(f"""
                            **Avg Resources:**  
                            CPU: {avg_cpu:.1f}% • GPU: {avg_gpu:.1f}% • RAM: {avg_ram:.1f}% • VRAM: {avg_vram:.1f}%
                            """)
                        
                        # Display the chat messages
                        display_chat_messages(messages)
    else:  # Tabs layout
        tabs = st.tabs(selected_models)
        
        for model, tab in zip(selected_models, tabs):
            with tab:
                for gpu in selected_gpus:
                    if model in all_logs[gpu]:
                        st.markdown(f"### {gpu}")
                        log_content = read_chat_log(all_logs[gpu][model])
                        if log_content.startswith("Error"):
                            st.error(log_content)
                            continue
                        
                        messages = parse_chat_log(log_content)
                        
                        # Chat Statistics at the top
                        user_messages = len([m for m in messages if m['role'] == "user"])
                        assistant_messages = len([m for m in messages if m['role'] == "assistant"])
                        
                        stat_cols = st.columns(4)
                        with stat_cols[0]:
                            st.metric("Total", len(messages))
                        with stat_cols[1]:
                            st.metric("User", user_messages)
                        with stat_cols[2]:
                            st.metric("Assistant", assistant_messages)
                        
                        # Average Resource Usage
                        if any(m.get('metrics') for m in messages):
                            metrics = [m['metrics'] for m in messages if m.get('metrics')]
                            avg_cpu = sum(m['cpu'] for m in metrics) / len(metrics)
                            avg_gpu = sum(m['gpu'] for m in metrics) / len(metrics)
                            avg_ram = sum(m['ram'] for m in metrics) / len(metrics)
                            avg_vram = sum(m['vram'] for m in metrics) / len(metrics)
                            
                            st.markdown(f"""
                            **Avg Resources:**  
                            CPU: {avg_cpu:.1f}% • GPU: {avg_gpu:.1f}% • RAM: {avg_ram:.1f}% • VRAM: {avg_vram:.1f}%
                            """)
                        
                        # Display the chat messages
                        display_chat_messages(messages)
                        
                        st.markdown("---")
else:
    st.info("Please select at least one GPU and one model to view chat logs.")

# Footer
st.markdown("---")
st.markdown("💬 Chat log viewer for examining LLM responses") 