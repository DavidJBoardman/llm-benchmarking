import streamlit as st
import pandas as pd
from utils.db import SessionLocal, ChatAudit
from sqlalchemy import func

st.set_page_config(layout="wide", page_title="LLM Chat Audit History")

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
    .stats-card {
        background-color: #2d3748;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Chat Audit History")

# Initialize database session
db = SessionLocal()

# Sidebar filters
st.sidebar.title("Filters")

# Model filter
models = [r[0] for r in db.query(ChatAudit.model_name).distinct()]
selected_models = st.sidebar.multiselect(
    "Select Models",
    models,
    default=models
)

# GPU filter
gpus = [r[0] for r in db.query(ChatAudit.gpu_name).distinct()]
selected_gpus = st.sidebar.multiselect(
    "Select GPUs",
    gpus,
    default=gpus
)

# Response quality filter
response_quality = st.sidebar.radio(
    "Response Quality",
    ["All", "Good", "Bad"]
)

# Build query
query = db.query(ChatAudit)
if selected_models:
    query = query.filter(ChatAudit.model_name.in_(selected_models))
if selected_gpus:
    query = query.filter(ChatAudit.gpu_name.in_(selected_gpus))
if response_quality != "All":
    query = query.filter(ChatAudit.is_good_response == (response_quality == "Good"))

# Get results
results = query.order_by(ChatAudit.created_at.desc()).all()

# Display statistics
st.header("📈 Statistics")

# Calculate statistics
total_audits = len(results)
good_responses = len([r for r in results if r.is_good_response])
bad_responses = total_audits - good_responses

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(
        f"""<div class="stats-card">
            <h3>Total Audits</h3>
            <h2>{total_audits}</h2>
        </div>""",
        unsafe_allow_html=True
    )
with col2:
    st.markdown(
        f"""<div class="stats-card">
            <h3>Good Responses</h3>
            <h2>{good_responses} ({good_responses/total_audits*100:.1f}%)</h2>
        </div>""",
        unsafe_allow_html=True
    )
with col3:
    st.markdown(
        f"""<div class="stats-card">
            <h3>Bad Responses</h3>
            <h2>{bad_responses} ({bad_responses/total_audits*100:.1f}%)</h2>
        </div>""",
        unsafe_allow_html=True
    )

# Display performance by model
st.subheader("Model Performance")
model_stats = {}
for model in selected_models:
    model_results = [r for r in results if r.model_name == model]
    if model_results:
        total = len(model_results)
        good = len([r for r in model_results if r.is_good_response])
        model_stats[model] = {
            'Total': total,
            'Good': good,
            'Bad': total - good,
            'Success Rate': f"{(good/total*100):.1f}%"
        }

st.dataframe(pd.DataFrame(model_stats).T)

# Display audit history
st.header("🔍 Audit History")

for result in results:
    st.markdown("---")
    
    # Header with metadata
    st.markdown(f"**Model:** {result.model_name} | **GPU:** {result.gpu_name} | **Created:** {result.created_at}")
    
    # User message
    st.markdown(
        f"""<div class="chat-message user-message">
            <strong>User:</strong>
            {result.user_message}
            </div>
            """,
        unsafe_allow_html=True
    )
    
    # Assistant message
    st.markdown(
        f"""<div class="chat-message assistant-message">
            <strong>Assistant:</strong>
            {result.assistant_message}
            </div>
            """,
        unsafe_allow_html=True
    )
    
    # Metrics
    st.markdown(
        f"""<div class="metrics-text">
            CPU: {result.cpu_usage}% • 
            GPU: {result.gpu_usage}% • 
            RAM: {result.ram_usage}% • 
            VRAM: {result.vram_usage:.2f}%
            </div>
            """,
        unsafe_allow_html=True
    )
    
    # Audit result
    st.info(f"Response Quality: {'✅ Good' if result.is_good_response else '❌ Bad'}")
    if result.feedback:
        st.text(f"Feedback: {result.feedback}")

# Close database session
db.close()

# Footer
st.markdown("---")
st.markdown("📊 Chat audit history and statistics") 