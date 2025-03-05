import streamlit as st
import pandas as pd
from pathlib import Path
import re
import os
import uuid
from datetime import datetime
from utils.db import SessionLocal, ChatAudit, get_all_gpus, get_all_llm_models, add_custom_gpu, add_custom_llm_model, delete_audit, update_audit
from utils.file_storage import write_file, is_using_s3
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
    .custom-input {
        background-color: #2d3748;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border-left: 4px solid #4299e1;
    }
    .info-box {
        background-color: #2a4365;
        color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border-left: 4px solid #4299e1;
    }
    /* Button styling */
    .stButton button {
        width: 100%;
    }
    /* Edit button */
    [data-testid="stButton"] button[kind="secondary"]:contains("Edit") {
        background-color: #4299e1;
        color: white;
    }
    /* Delete button */
    [data-testid="stButton"] button[kind="secondary"]:contains("Delete") {
        background-color: #e53e3e;
        color: white;
    }
    /* Confirmation buttons */
    [data-testid="stButton"] button[kind="secondary"]:contains("Yes, Delete") {
        background-color: #e53e3e;
        color: white;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🔍 LLM Chat Audit")

# Check if database connection is available
db_available = SessionLocal is not None
if not db_available:
    st.error("Database connection is not available. Audit data will not be saved.")

# Check if S3 is available
if is_using_s3():
    st.markdown(
        """<div class="info-box">
            📤 S3 storage is enabled. Uploaded logs will be stored in S3.
        </div>""",
        unsafe_allow_html=True
    )

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

def save_log_file(content, filename=None, model_name=None, gpu_name=None):
    """Save log file to S3 or local storage with descriptive filename."""
    # Generate a unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    
    if filename and not (model_name and gpu_name):
        # If we have a filename but no model/gpu info, keep the original name for local storage
        local_filename = filename
    else:
        # For local storage, use a simple format if no model/gpu provided
        local_filename = f"log_{timestamp}_{unique_id}.txt"
    
    # For S3, create a more descriptive filename with model and GPU info if available
    if is_using_s3() and model_name and gpu_name:
        # Clean up model and GPU names for filename (remove special chars)
        clean_model = re.sub(r'[^\w\-]', '_', model_name)
        clean_gpu = re.sub(r'[^\w\-]', '_', gpu_name)
        s3_filename = f"{clean_gpu}_{clean_model}_{timestamp}_{unique_id}.txt"
    else:
        s3_filename = local_filename
    
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    if not logs_dir.exists():
        logs_dir.mkdir(parents=True)
    
    # Save file using the storage utility
    local_file_path = os.path.join(logs_dir, local_filename)
    
    # If using S3, specify the S3 key with the descriptive filename
    if is_using_s3():
        s3_key = os.path.join("logs", s3_filename)
        saved_path = write_file(content, local_file_path, s3_key=s3_key)
    else:
        saved_path = write_file(content, local_file_path)
    
    return saved_path

# File uploader
uploaded_file = st.file_uploader("Upload a chat log file", type=['txt'])

if uploaded_file is not None:
    # Read and parse the log file
    try:
        content = uploaded_file.getvalue().decode()
        
        # Get selected model and GPU
        model_name = st.session_state.get('model_name', '')
        gpu_name = st.session_state.get('gpu_name', '')
        
        # Save the log file to S3 or locally
        log_path = save_log_file(content, filename=uploaded_file.name, model_name=model_name, gpu_name=gpu_name)
        
        if log_path:
            if log_path.startswith("s3://"):
                st.success(f"Log file uploaded to S3: {log_path}")
            else:
                st.success(f"Log file saved locally: {log_path}")
        
        conversations = parse_chat_log(content)
        
        # Get available models and GPUs from the database
        available_models = get_all_llm_models()
        available_gpus = get_all_gpus()
        
        # Model selection with custom option
        st.subheader("Select or Add Model")
        col1, col2 = st.columns([3, 1])
        
        with col1:
            model_options = [""] + [model.name for model in available_models]
            model_name = st.selectbox(
                "Select Model",
                model_options,
                index=0,
                key="model_name"
            )
        
        with col2:
            use_custom_model = st.checkbox("Add Custom Model")
        
        if use_custom_model:
            st.markdown('<div class="custom-input">', unsafe_allow_html=True)
            custom_model_name = st.text_input("Enter Custom Model Name")
            if st.button("Add Model"):
                if custom_model_name:
                    new_model = add_custom_llm_model(custom_model_name)
                    if new_model:
                        st.success(f"Added new model: {custom_model_name}")
                        # Refresh the page to update the model list
                        st.experimental_rerun()
                    else:
                        st.error("Failed to add custom model")
                else:
                    st.warning("Please enter a model name")
            st.markdown('</div>', unsafe_allow_html=True)
            
        # GPU selection with custom option
        st.subheader("Select or Add GPU")
        col1, col2 = st.columns([3, 1])
        
        with col1:
            gpu_options = [""] + [gpu.name for gpu in available_gpus]
            gpu_name = st.selectbox(
                "Select GPU",
                gpu_options,
                index=0,
                key="gpu_name"
            )
        
        with col2:
            use_custom_gpu = st.checkbox("Add Custom GPU")
        
        if use_custom_gpu:
            st.markdown('<div class="custom-input">', unsafe_allow_html=True)
            custom_gpu_name = st.text_input("Enter Custom GPU Name")
            if st.button("Add GPU"):
                if custom_gpu_name:
                    new_gpu = add_custom_gpu(custom_gpu_name)
                    if new_gpu:
                        st.success(f"Added new GPU: {custom_gpu_name}")
                        # Refresh the page to update the GPU list
                        st.experimental_rerun()
                    else:
                        st.error("Failed to add custom GPU")
                else:
                    st.warning("Please enter a GPU name")
            st.markdown('</div>', unsafe_allow_html=True)
        
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
                        if not db_available:
                            st.warning("Database is not available. Audit data cannot be saved.")
                        else:
                            try:
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
                            except Exception as e:
                                st.error(f"Error saving audit: {str(e)}")
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")

# Footer
st.markdown("---")

# Add a section for recent audits
if db_available:
    st.header("Recent Audits")
    st.markdown("View, edit, or delete your recent audit submissions.")
    
    try:
        # Get recent audits (last 5)
        db = SessionLocal()
        recent_audits = db.query(ChatAudit).order_by(ChatAudit.created_at.desc()).limit(5).all()
        
        if recent_audits:
            for audit in recent_audits:
                st.markdown("---")
                
                # Header with metadata
                st.markdown(
                    f"**Audit #{audit.id}** | **Model:** {audit.model_name} | "
                    f"**GPU:** {audit.gpu_name} | "
                    f"**Created:** {audit.created_at}",
                    unsafe_allow_html=True
                )
                
                # User message
                st.markdown(
                    f"""<div class="chat-message user-message">
                        <strong>User:</strong>
                        {audit.user_message}
                        </div>
                        """,
                    unsafe_allow_html=True
                )
                
                # Assistant message
                st.markdown(
                    f"""<div class="chat-message assistant-message">
                        <strong>Assistant:</strong>
                        {audit.assistant_message}
                        </div>
                        """,
                    unsafe_allow_html=True
                )
                
                # Audit result
                st.info(f"Response Quality: {'✅ Good' if audit.is_good_response else '❌ Bad'}")
                if audit.feedback:
                    st.text(f"Feedback: {audit.feedback}")
                
                # Add edit and delete buttons
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    if st.button(f"Edit Audit #{audit.id}", key=f"edit_{audit.id}"):
                        st.session_state[f"edit_mode_{audit.id}"] = True
                
                with col2:
                    if st.button(f"Delete Audit #{audit.id}", key=f"delete_{audit.id}"):
                        st.session_state[f"delete_confirm_{audit.id}"] = True
                
                # Edit form
                if st.session_state.get(f"edit_mode_{audit.id}", False):
                    with st.form(key=f"edit_form_{audit.id}"):
                        st.subheader(f"Edit Audit #{audit.id}")
                        
                        # Edit fields
                        edited_user_message = st.text_area("User Message", value=audit.user_message, key=f"edit_user_{audit.id}")
                        edited_assistant_message = st.text_area("Assistant Message", value=audit.assistant_message, key=f"edit_assistant_{audit.id}")
                        edited_is_good = st.radio(
                            "Is this a good response?",
                            ["Yes", "No"],
                            index=0 if audit.is_good_response else 1,
                            key=f"edit_is_good_{audit.id}"
                        )
                        edited_feedback = st.text_area("Feedback", value=audit.feedback or "", key=f"edit_feedback_{audit.id}")
                        
                        col1, col2 = st.columns([1, 1])
                        with col1:
                            submit = st.form_submit_button("Save Changes")
                        with col2:
                            cancel = st.form_submit_button("Cancel")
                        
                        if submit:
                            # Update the audit
                            updated = update_audit(
                                audit.id,
                                user_message=edited_user_message,
                                assistant_message=edited_assistant_message,
                                is_good_response=(edited_is_good == "Yes"),
                                feedback=edited_feedback
                            )
                            
                            if updated:
                                st.success(f"Audit #{audit.id} updated successfully!")
                                # Clear edit mode
                                st.session_state.pop(f"edit_mode_{audit.id}", None)
                                # Refresh the page
                                st.experimental_rerun()
                            else:
                                st.error("Failed to update audit. Please try again.")
                        
                        if cancel:
                            # Clear edit mode
                            st.session_state.pop(f"edit_mode_{audit.id}", None)
                            st.experimental_rerun()
                
                # Delete confirmation
                if st.session_state.get(f"delete_confirm_{audit.id}", False):
                    st.warning(f"Are you sure you want to delete Audit #{audit.id}? This action cannot be undone.")
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        if st.button(f"Yes, Delete Audit #{audit.id}", key=f"confirm_delete_{audit.id}"):
                            # Delete the audit
                            success = delete_audit(audit.id)
                            
                            if success:
                                st.success(f"Audit #{audit.id} deleted successfully!")
                                # Clear delete confirmation
                                st.session_state.pop(f"delete_confirm_{audit.id}", None)
                                # Refresh the page
                                st.experimental_rerun()
                            else:
                                st.error("Failed to delete audit. Please try again.")
                    
                    with col2:
                        if st.button("Cancel", key=f"cancel_delete_{audit.id}"):
                            # Clear delete confirmation
                            st.session_state.pop(f"delete_confirm_{audit.id}", None)
                            st.experimental_rerun()
        else:
            st.info("No recent audits found. Submit some audits to see them here.")
        
        # Close database session
        db.close()
    except Exception as e:
        st.error(f"Error retrieving recent audits: {str(e)}")

st.markdown("---")
st.markdown("🔍 Chat audit tool for evaluating LLM responses") 