"""
Guardrails Configuration and Management
Handles safety and validation for LLM inputs and outputs
"""
import os
from typing import Dict, Any, Optional, List
import streamlit as st
from guardrails import Guard
from guardrails.hub import ToxicLanguage, ProfanityFree, ReadingTime, SensitiveTopics
from guardrails.validators import ValidLength, ValidChoices
from pydantic import BaseModel, Field


class GuardrailsConfig:
    """Configuration for Guardrails AI safety measures"""
    
    def __init__(self):
        self.enabled = os.getenv("GUARDRAILS_ENABLED", "true").lower() == "true"
        self.guards = {}
        self._initialize_guards()
    
    def _initialize_guards(self):
        """Initialize different types of guards for various use cases"""
        try:
            if not self.enabled:
                return
            
            # Input validation guard
            self.guards["input_safety"] = self._create_input_safety_guard()
            
            # Output validation guard
            self.guards["output_quality"] = self._create_output_quality_guard()
            
            # Content moderation guard
            self.guards["content_moderation"] = self._create_content_moderation_guard()
            
            # Structured output guard
            self.guards["structured_output"] = self._create_structured_output_guard()
            
        except Exception as e:
            # Fail silently - guardrails should not break the app
            if os.getenv("STREAMLIT_ENV") != "production":
                st.warning(f"⚠️ Guardrails initialization failed: {e}")
            self.enabled = False
    
    def _create_input_safety_guard(self) -> Guard:
        """Create guard for input safety validation"""
        try:
            return Guard().use(
                ToxicLanguage(threshold=0.8, validation_method="sentence"),
                ProfanityFree(),
                ValidLength(min=1, max=2000)
            )
        except Exception:
            return None
    
    def _create_output_quality_guard(self) -> Guard:
        """Create guard for output quality validation"""
        try:
            return Guard().use(
                ValidLength(min=10, max=5000),
                ReadingTime(reading_time_range=(1, 300))  # 1-300 seconds reading time
            )
        except Exception:
            return None
    
    def _create_content_moderation_guard(self) -> Guard:
        """Create guard for content moderation"""
        try:
            sensitive_topics = [
                "violence", "hate_speech", "harassment", 
                "illegal_activities", "self_harm"
            ]
            return Guard().use(
                SensitiveTopics(sensitive_topics=sensitive_topics, threshold=0.8),
                ToxicLanguage(threshold=0.7, validation_method="full")
            )
        except Exception:
            return None
    
    def _create_structured_output_guard(self) -> Guard:
        """Create guard for structured output validation"""
        try:
            class ChatResponse(BaseModel):
                content: str = Field(description="The main response content")
                confidence: float = Field(ge=0.0, le=1.0, description="Confidence score")
                safe: bool = Field(description="Whether the response is safe")
            
            return Guard.from_pydantic(ChatResponse)
        except Exception:
            return None
    
    def get_guard(self, guard_type: str) -> Optional[Guard]:
        """Get a specific guard by type"""
        if not self.enabled:
            return None
        return self.guards.get(guard_type)
    
    def is_enabled(self) -> bool:
        """Check if guardrails are enabled"""
        return self.enabled and len(self.guards) > 0


# Global instance
guardrails_config = GuardrailsConfig()