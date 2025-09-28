"""
Monitoring Dashboard Component
Shows LLM usage statistics and costs in Streamlit
"""
import streamlit as st
import os
from typing import Dict, Any, List
from datetime import datetime, timedelta
from .langfuse_integration import langfuse_manager


def show_monitoring_dashboard():
    """Display monitoring dashboard in Streamlit sidebar"""
    try:
        if not langfuse_manager.is_enabled():
            return
        
        with st.sidebar:
            st.subheader("📊 LLM Monitoring")
            
            # Dashboard link
            dashboard_url = langfuse_manager.get_dashboard_url()
            st.markdown(f"[📈 Open Langfuse Dashboard]({dashboard_url})")
            
            # Quick stats (if available)
            try:
                # Note: This would require additional Langfuse API calls
                # For now, we'll show basic info
                st.metric("Status", "🟢 Active")
                st.metric("Session", st.session_state.get("session_id", "N/A"))
                
            except Exception:
                # Silently fail if stats can't be loaded
                pass
                
    except Exception:
        # Dashboard should never break the main app
        pass


def create_session_id() -> str:
    """Create a unique session ID for tracking"""
    if "session_id" not in st.session_state:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.session_state.session_id = f"session_{timestamp}"
    
    return st.session_state.session_id


def log_user_interaction(usecase: str, user_message: str, response: str):
    """Log user interaction for monitoring - fails silently if monitoring unavailable"""
    try:
        if not langfuse_manager.is_enabled():
            return
        
        session_id = create_session_id()
        
        # Create trace for this interaction
        trace = langfuse_manager.create_trace(
            name=f"chat_interaction_{usecase}",
            session_id=session_id,
            user_id="streamlit_user",
            metadata={
                "usecase": usecase,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        if trace:
            # Log the generation
            langfuse_manager.log_generation(
                trace_id=trace.id,
                model="groq_llm",
                input_text=user_message,
                output_text=response,
                metadata={
                    "usecase": usecase,
                    "session_id": session_id
                }
            )
            
    except Exception:
        # Silently fail - logging should never break the app
        pass


def show_cost_tracking():
    """Show cost tracking information"""
    try:
        if not langfuse_manager.is_enabled():
            return
        
        st.info("💰 Cost tracking is enabled via Langfuse. View detailed costs in the dashboard.")
    except Exception:
        # Silently fail if cost tracking info can't be shown
        pass