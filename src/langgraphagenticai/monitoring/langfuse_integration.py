"""
Langfuse Integration for LLM Monitoring and Cost Tracking
"""
import os
from typing import Optional, Dict, Any
import streamlit as st
from langfuse import Langfuse
from langfuse.langchain import CallbackHandler
from langchain.callbacks.base import BaseCallbackHandler


class LangfuseManager:
    """Manages Langfuse connection and monitoring"""
    
    def __init__(self):
        self.langfuse = None
        self.callback_handler = None
        self._initialize_langfuse()
    
    def _initialize_langfuse(self):
        """Initialize Langfuse client with graceful fallback"""
        try:
            secret_key = os.getenv("LANGFUSE_SECRET_KEY")
            public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
            host = os.getenv("LANGFUSE_HOST", "http://localhost:3000")
            
            if not secret_key or not public_key:
                # Silently disable monitoring if keys are not provided
                return
            
            # Initialize Langfuse with timeout
            self.langfuse = Langfuse(
                secret_key=secret_key,
                public_key=public_key,
                host=host,
                timeout=5  # 5 second timeout
            )
            
            # Create callback handler for LangChain integration
            self.callback_handler = CallbackHandler(
                secret_key=secret_key,
                public_key=public_key,
                host=host,
                timeout=5
            )
            
            # Test connection with timeout
            try:
                self.langfuse.auth_check()
                # Only show success message if in development mode
                if os.getenv("STREAMLIT_ENV") != "production":
                    st.success("✅ Langfuse monitoring enabled")
            except Exception as auth_error:
                # Connection test failed, disable monitoring
                self.langfuse = None
                self.callback_handler = None
                if os.getenv("STREAMLIT_ENV") != "production":
                    st.warning(f"⚠️ Langfuse connection failed: {auth_error}. Monitoring disabled.")
                
        except Exception as e:
            # Any initialization error should not break the app
            self.langfuse = None
            self.callback_handler = None
            # Only log in development mode
            if os.getenv("STREAMLIT_ENV") != "production":
                st.info("ℹ️ Langfuse monitoring not available")
    
    def get_callback_handler(self) -> Optional[BaseCallbackHandler]:
        """Get the Langfuse callback handler for LangChain"""
        return self.callback_handler
    
    def is_enabled(self) -> bool:
        """Check if Langfuse monitoring is enabled"""
        return self.langfuse is not None and self.callback_handler is not None
    
    def create_trace(self, name: str, user_id: Optional[str] = None, 
                    session_id: Optional[str] = None, **kwargs) -> Optional[Any]:
        """Create a new trace for monitoring"""
        if not self.langfuse:
            return None
            
        try:
            return self.langfuse.trace(
                name=name,
                user_id=user_id,
                session_id=session_id,
                **kwargs
            )
        except Exception:
            # Silently fail - monitoring should never break the app
            return None
    
    def log_generation(self, trace_id: str, model: str, input_text: str, 
                      output_text: str, **kwargs):
        """Log a generation event"""
        if not self.langfuse:
            return
            
        try:
            self.langfuse.generation(
                trace_id=trace_id,
                name="llm_generation",
                model=model,
                input=input_text,
                output=output_text,
                **kwargs
            )
        except Exception:
            # Silently fail - monitoring should never break the app
            pass
    
    def get_dashboard_url(self) -> str:
        """Get the Langfuse dashboard URL"""
        host = os.getenv("LANGFUSE_HOST", "http://localhost:3000")
        return f"{host}/project/default"


# Global instance
langfuse_manager = LangfuseManager()


def get_langfuse_callbacks():
    """Get Langfuse callbacks for LangChain integration"""
    if langfuse_manager.is_enabled():
        return [langfuse_manager.get_callback_handler()]
    return []


def create_monitored_llm(llm, session_id: Optional[str] = None):
    """Wrap an LLM with Langfuse monitoring - gracefully falls back if monitoring unavailable"""
    try:
        if not langfuse_manager.is_enabled():
            return llm
        
        # Add Langfuse callback to the LLM
        callbacks = get_langfuse_callbacks()
        if callbacks:
            # Create a new LLM instance with callbacks
            llm_with_callbacks = llm.__class__(**llm.__dict__)
            llm_with_callbacks.callbacks = callbacks
            return llm_with_callbacks
        
        return llm
    except Exception:
        # If anything goes wrong with monitoring, return original LLM
        return llm