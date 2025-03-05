import streamlit as st
import pandas as pd
from utils.db import SessionLocal, ChatAudit, get_all_gpus, get_all_llm_models, delete_audit, update_audit
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
    .custom-tag {
        background-color: #4299e1;
        color: white;
        padding: 0.1rem 0.4rem;
        border-radius: 0.3rem;
        font-size: 0.8em;
        margin-left: 0.5rem;
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

st.title("📊 Chat Audit History")

# Check if database connection is available
if SessionLocal is None:
    st.error("Database connection is not available. This page requires a database connection to function.")
    st.stop()

try:
    # Initialize database session
    db = SessionLocal()

    # Sidebar filters
    st.sidebar.title("Filters")

    try:
        # Get all models and GPUs from the database
        available_models = get_all_llm_models()
        available_gpus = get_all_gpus()
        
        # If no models or GPUs are available from the database, fall back to querying distinct values from audit table
        if not available_models:
            models = [r[0] for r in db.query(ChatAudit.model_name).distinct()]
        else:
            models = [model.name for model in available_models]
        
        if not available_gpus:
            gpus = [r[0] for r in db.query(ChatAudit.gpu_name).distinct()]
        else:
            gpus = [gpu.name for gpu in available_gpus]
        
        # Create dictionaries to track which models and GPUs are custom
        custom_models = {model.name: model.is_custom for model in available_models}
        custom_gpus = {gpu.name: gpu.is_custom for gpu in available_gpus}
        
        # Model filter
        selected_models = st.sidebar.multiselect(
            "Select Models",
            models,
            default=models
        )

        # GPU filter
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
        
        # Custom entries filter
        show_custom_only = st.sidebar.checkbox("Show Custom Entries Only")

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
        
        # Filter for custom entries if requested
        if show_custom_only:
            results = [r for r in results if 
                      (r.model_name in custom_models and custom_models[r.model_name]) or 
                      (r.gpu_name in custom_gpus and custom_gpus[r.gpu_name])]

        # Display statistics
        st.header("📈 Statistics")

        # Calculate statistics
        total_audits = len(results)
        
        if total_audits > 0:
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
                        'Success Rate': f"{(good/total*100):.1f}%",
                        'Is Custom': model in custom_models and custom_models[model]
                    }

            # Convert to DataFrame and display
            model_df = pd.DataFrame(model_stats).T
            
            # Display the DataFrame with custom styling
            st.dataframe(model_df)
            
            # Display custom model indicators
            custom_models_list = [model for model in selected_models if model in custom_models and custom_models[model]]
            if custom_models_list:
                st.markdown("**Custom Models:** " + ", ".join([f"<span class='custom-tag'>{model}</span>" for model in custom_models_list]), unsafe_allow_html=True)

            # Display performance by GPU
            st.subheader("GPU Performance")
            gpu_stats = {}
            for gpu in selected_gpus:
                gpu_results = [r for r in results if r.gpu_name == gpu]
                if gpu_results:
                    total = len(gpu_results)
                    good = len([r for r in gpu_results if r.is_good_response])
                    gpu_stats[gpu] = {
                        'Total': total,
                        'Good': good,
                        'Bad': total - good,
                        'Success Rate': f"{(good/total*100):.1f}%",
                        'Is Custom': gpu in custom_gpus and custom_gpus[gpu]
                    }

            # Convert to DataFrame and display
            gpu_df = pd.DataFrame(gpu_stats).T
            st.dataframe(gpu_df)
            
            # Display custom GPU indicators
            custom_gpus_list = [gpu for gpu in selected_gpus if gpu in custom_gpus and custom_gpus[gpu]]
            if custom_gpus_list:
                st.markdown("**Custom GPUs:** " + ", ".join([f"<span class='custom-tag'>{gpu}</span>" for gpu in custom_gpus_list]), unsafe_allow_html=True)

            # Display audit history
            st.header("🔍 Audit History")

            for result in results:
                st.markdown("---")
                
                # Header with metadata and custom tags
                model_tag = f"<span class='custom-tag'>Custom</span>" if result.model_name in custom_models and custom_models[result.model_name] else ""
                gpu_tag = f"<span class='custom-tag'>Custom</span>" if result.gpu_name in custom_gpus and custom_gpus[result.gpu_name] else ""
                
                st.markdown(
                    f"**Model:** {result.model_name} {model_tag} | "
                    f"**GPU:** {result.gpu_name} {gpu_tag} | "
                    f"**Created:** {result.created_at}",
                    unsafe_allow_html=True
                )
                
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
                
                # Add edit and delete buttons
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    if st.button(f"Edit Audit #{result.id}", key=f"edit_{result.id}"):
                        st.session_state[f"edit_mode_{result.id}"] = True
                
                with col2:
                    if st.button(f"Delete Audit #{result.id}", key=f"delete_{result.id}"):
                        st.session_state[f"delete_confirm_{result.id}"] = True
                
                # Edit form
                if st.session_state.get(f"edit_mode_{result.id}", False):
                    with st.form(key=f"edit_form_{result.id}"):
                        st.subheader(f"Edit Audit #{result.id}")
                        
                        # Edit fields
                        edited_user_message = st.text_area("User Message", value=result.user_message, key=f"edit_user_{result.id}")
                        edited_assistant_message = st.text_area("Assistant Message", value=result.assistant_message, key=f"edit_assistant_{result.id}")
                        edited_is_good = st.radio(
                            "Is this a good response?",
                            ["Yes", "No"],
                            index=0 if result.is_good_response else 1,
                            key=f"edit_is_good_{result.id}"
                        )
                        edited_feedback = st.text_area("Feedback", value=result.feedback or "", key=f"edit_feedback_{result.id}")
                        
                        col1, col2 = st.columns([1, 1])
                        with col1:
                            submit = st.form_submit_button("Save Changes")
                        with col2:
                            cancel = st.form_submit_button("Cancel")
                        
                        if submit:
                            # Update the audit
                            updated = update_audit(
                                result.id,
                                user_message=edited_user_message,
                                assistant_message=edited_assistant_message,
                                is_good_response=(edited_is_good == "Yes"),
                                feedback=edited_feedback
                            )
                            
                            if updated:
                                st.success(f"Audit #{result.id} updated successfully!")
                                # Clear edit mode
                                st.session_state.pop(f"edit_mode_{result.id}", None)
                                # Refresh the page
                                st.experimental_rerun()
                            else:
                                st.error("Failed to update audit. Please try again.")
                        
                        if cancel:
                            # Clear edit mode
                            st.session_state.pop(f"edit_mode_{result.id}", None)
                            st.experimental_rerun()
                
                # Delete confirmation
                if st.session_state.get(f"delete_confirm_{result.id}", False):
                    st.warning(f"Are you sure you want to delete Audit #{result.id}? This action cannot be undone.")
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        if st.button(f"Yes, Delete Audit #{result.id}", key=f"confirm_delete_{result.id}"):
                            # Delete the audit
                            success = delete_audit(result.id)
                            
                            if success:
                                st.success(f"Audit #{result.id} deleted successfully!")
                                # Clear delete confirmation
                                st.session_state.pop(f"delete_confirm_{result.id}", None)
                                # Refresh the page
                                st.experimental_rerun()
                            else:
                                st.error("Failed to delete audit. Please try again.")
                    
                    with col2:
                        if st.button("Cancel", key=f"cancel_delete_{result.id}"):
                            # Clear delete confirmation
                            st.session_state.pop(f"delete_confirm_{result.id}", None)
                            st.experimental_rerun()
        else:
            st.info("No audit data found with the current filters. Try changing your filter settings or add some audits first.")
    except Exception as e:
        st.error(f"Error querying database: {str(e)}")
    finally:
        # Close database session
        db.close()
except Exception as e:
    st.error(f"Error connecting to database: {str(e)}")

# Footer
st.markdown("---")
st.markdown("📊 Chat audit history and statistics") 