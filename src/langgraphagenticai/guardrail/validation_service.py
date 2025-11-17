"""
Guardrails Validation Service
Provides validation methods for inputs and outputs
"""
from typing import Dict, Any, Optional, Tuple
from .guardrails_config import guardrails_config


class ValidationService:
    """Service for validating inputs and outputs using Guardrails"""
    
    def __init__(self):
        self.config = guardrails_config
    
    def validate_user_input(self, user_input: str) -> Tuple[bool, str, Optional[str]]:
        """
        Validate user input for safety and appropriateness
        
        Returns:
            Tuple[bool, str, Optional[str]]: (is_valid, processed_input, error_message)
        """
        try:
            if not self.config.is_enabled():
                return True, user_input, None
            
            # Get input safety guard
            guard = self.config.get_guard("input_safety")
            if not guard:
                return True, user_input, None
            
            # Validate input
            result = guard.validate(user_input)
            
            if result.validation_passed:
                return True, result.validated_output, None
            else:
                # Extract error messages
                errors = []
                for failure in result.validation_failures:
                    errors.append(failure.error_message)
                
                error_msg = "Input validation failed: " + "; ".join(errors)
                return False, user_input, error_msg
                
        except Exception as e:
            # Fail silently - validation should not break the app
            return True, user_input, None
    
    def validate_llm_output(self, llm_output: str, usecase: str = "general") -> Tuple[bool, str, Optional[str]]:
        """
        Validate LLM output for quality and safety
        
        Returns:
            Tuple[bool, str, Optional[str]]: (is_valid, processed_output, error_message)
        """
        try:
            if not self.config.is_enabled():
                return True, llm_output, None
            
            # Get appropriate guard based on use case
            if usecase in ["MCP Chatbot", "Chatbot with Tool"]:
                guard = self.config.get_guard("content_moderation")
            else:
                guard = self.config.get_guard("output_quality")
            
            if not guard:
                return True, llm_output, None
            
            # Validate output
            result = guard.validate(llm_output)
            
            if result.validation_passed:
                return True, result.validated_output, None
            else:
                # Extract error messages
                errors = []
                for failure in result.validation_failures:
                    errors.append(failure.error_message)
                
                error_msg = "Output validation failed: " + "; ".join(errors)
                
                # Return a safe fallback message
                safe_output = "I apologize, but I cannot provide a response that meets safety guidelines. Please try rephrasing your question."
                return False, safe_output, error_msg
                
        except Exception as e:
            # Fail silently - validation should not break the app
            return True, llm_output, None
    
    def moderate_content(self, content: str) -> Tuple[bool, Optional[str]]:
        """
        Moderate content for sensitive topics and harmful content
        
        Returns:
            Tuple[bool, Optional[str]]: (is_safe, warning_message)
        """
        try:
            if not self.config.is_enabled():
                return True, None
            
            guard = self.config.get_guard("content_moderation")
            if not guard:
                return True, None
            
            result = guard.validate(content)
            
            if result.validation_passed:
                return True, None
            else:
                # Extract warning messages
                warnings = []
                for failure in result.validation_failures:
                    warnings.append(failure.error_message)
                
                warning_msg = "Content moderation warning: " + "; ".join(warnings)
                return False, warning_msg
                
        except Exception as e:
            # Fail silently
            return True, None
    
    def get_validation_stats(self) -> Dict[str, Any]:
        """Get validation statistics"""
        try:
            if not self.config.is_enabled():
                return {"enabled": False}
            
            return {
                "enabled": True,
                "guards_available": list(self.config.guards.keys()),
                "total_guards": len(self.config.guards)
            }
        except Exception:
            return {"enabled": False}


# Global instance
validation_service = ValidationService()