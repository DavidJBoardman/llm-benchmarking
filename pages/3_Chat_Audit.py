import streamlit as st
import pandas as pd
from pathlib import Path
import re
from utils.db import SessionLocal, ChatAudit
import io

st.set_page_config(layout="wide", page_title="LLM Chat Audit")

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
    .metrics-text {
        color: #a0aec0;
        margin-top: 0.5rem;
        text-align: right;
        font-size: 0.85em;
    }
    .audit-form {
        background-color: #2d3748;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .warning-message {
        background-color: #744210;
        color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border-left: 4px solid #d69e2e;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🔍 LLM Chat Audit")

def parse_chat_log(content):
    # Regular expressions for parsing
    user_query_pattern = r'\[DEBUG\]\[User \| .*?\]: querying model with prompt: (.*?)(?=cpu usage)'
    system_metrics_pattern = r'cpu usage: (.*?)%\ngpu usage: (.*?)%\nram usage: (.*?)%\nvram usage: (.*?)%'
    response_pattern = r'\[DEBUG\]\[User \| .*?\]: unformated response: (.*?)(?=cpu usage|\[INFO\]|$)'
    
    # Find all user queries with their timestamps
    user_queries = re.finditer(user_query_pattern, content, re.DOTALL)
    responses = re.finditer(response_pattern, content, re.DOTALL)
    
    # Combine queries and responses
    conversation = []
    
    for query, response in zip(user_queries, responses):
        # Get the user message
        user_text = query.group(1).strip()
        response_text = response.group(1).strip()
        
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
            'user_message': user_text,
            'assistant_message': response_text,
            'metrics': metrics
        })
    
    return conversation

# File uploader
uploaded_file = st.file_uploader("Upload a chat log file", type=['txt'])

if uploaded_file is not None:
    # Read and parse the log file
    content = uploaded_file.getvalue().decode()
    conversations = parse_chat_log(content)
    
    # Model selection
    model_name = st.selectbox(
        "Select Model",
        ["", "llama3-latest", "llama3-8b-instruct", "llama2-7b-chat"],
        index=0
    )
    
    # GPU selection
    gpu_name = st.selectbox(
        "Select GPU",
        ["", "RTX 4090", "RTX 4080S", "ADA 6000"],
        index=0
    )
    
    if not model_name or not gpu_name:
        st.markdown(
            """<div class="warning-message">
                ⚠️ Please select both a GPU and model name to proceed with the audit.
            </div>""",
            unsafe_allow_html=True
        )
    else:
        # Display conversations and collect feedback
        for idx, conv in enumerate(conversations):
            st.markdown("---")
            st.markdown(f"### Conversation {idx + 1}")
            
            # Display user message
            st.markdown(
                f"""<div class="chat-message user-message">
                    <strong>User:</strong>
                    {conv['user_message']}
                    </div>
                    """,
                unsafe_allow_html=True
            )
            
            # Display assistant message
            st.markdown(
                f"""<div class="chat-message assistant-message">
                    <strong>Assistant:</strong>
                    {conv['assistant_message']}
                    </div>
                    """,
                unsafe_allow_html=True
            )
            
            # Display metrics if available
            if conv['metrics']:
                st.markdown(
                    f"""<div class="metrics-text">
                        CPU: {conv['metrics']['cpu']}% • 
                        GPU: {conv['metrics']['gpu']}% • 
                        RAM: {conv['metrics']['ram']}% • 
                        VRAM: {conv['metrics']['vram']:.2f}%
                        </div>
                        """,
                    unsafe_allow_html=True
                )
            
            # Audit form
            with st.form(f"audit_form_{idx}"):
                st.markdown('<div class="audit-form">', unsafe_allow_html=True)
                is_good = st.radio(
                    "Is this a good response?",
                    ["Yes", "No"],
                    key=f"is_good_{idx}"
                )
                feedback = st.text_area(
                    "Additional feedback (optional)",
                    key=f"feedback_{idx}"
                )
                submit_button = st.form_submit_button("Submit Audit")
                st.markdown('</div>', unsafe_allow_html=True)
                
                if submit_button:
                    # Save to database
                    db = SessionLocal()
                    chat_audit = ChatAudit(
                        model_name=model_name,
                        gpu_name=gpu_name,
                        user_message=conv['user_message'],
                        assistant_message=conv['assistant_message'],
                        is_good_response=(is_good == "Yes"),
                        feedback=feedback,
                        cpu_usage=conv['metrics']['cpu'] if conv['metrics'] else 0,
                        gpu_usage=conv['metrics']['gpu'] if conv['metrics'] else 0,
                        ram_usage=conv['metrics']['ram'] if conv['metrics'] else 0,
                        vram_usage=conv['metrics']['vram'] if conv['metrics'] else 0
                    )
                    db.add(chat_audit)
                    db.commit()
                    db.close()
                    st.success("Audit submitted successfully!")

# Footer
st.markdown("---")
st.markdown("🔍 Chat audit tool for evaluating LLM responses") 