"""
Guardrails LLM Wrapper
Wraps LLM calls with input/output validation
"""
from typing import Any, List, Optional, Dict
from langchain_core.language_models.base import BaseLanguageModel
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage
from langchain_core.callbacks import CallbackManagerForLLMRun
from .validation_service import validation_service
import streamlit as st


class GuardrailsLLMWrapper(BaseLanguageModel):
    """
    Wrapper that adds Guardrails validation to any LangChain LLM
    """
    
    def __init__(self, llm: BaseLanguageModel, usecase: str = "general"):
        self.llm = llm
        self.usecase = usecase
        self.validation_service = validation_service
    
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Any:
        """Generate response with input/output validation"""
        try:
            # Extract user input for validation
            user_input = ""
            if messages:
                last_message = messages[-1]
                if isinstance(last_message, HumanMessage):
                    user_input = last_message.content
            
            # Validate input
            if user_input:
                is_valid, processed_input, error_msg = self.validation_service.validate_user_input(user_input)
                
                if not is_valid:
                    # Show warning to user
                    if error_msg:
                        st.warning(f"🛡️ Input Safety: {error_msg}")
                    
                    # Return safe response
                    safe_response = "I cannot process this request due to safety guidelines. Please rephrase your question."
                    return self.llm._generate([HumanMessage(content=safe_response)], stop, run_manager, **kwargs)
                
                # Update message with processed input if it was modified
                if processed_input != user_input:
                    messages[-1] = HumanMessage(content=processed_input)
            
            # Call original LLM
            result = self.llm._generate(messages, stop, run_manager, **kwargs)
            
            # Validate output
            if result and hasattr(result, 'generations') and result.generations:
                for generation in result.generations:
                    if hasattr(generation, 'message') and hasattr(generation.message, 'content'):
                        output_content = generation.message.content
                        
                        is_valid, processed_output, error_msg = self.validation_service.validate_llm_output(
                            output_content, self.usecase
                        )
                        
                        if not is_valid:
                            # Show warning to user
                            if error_msg:
                                st.warning(f"🛡️ Output Safety: Response was filtered for safety")
                            
                            # Replace with processed (safe) output
                            generation.message.content = processed_output
            
            return result
            
        except Exception as e:
            # If validation fails, fall back to original LLM
            return self.llm._generate(messages, stop, run_manager, **kwargs)
    
    def invoke(self, input_data, config=None, **kwargs):
        """Invoke with validation"""
        try:
            # Handle different input types
            if isinstance(input_data, str):
                # Validate string input
                is_valid, processed_input, error_msg = self.validation_service.validate_user_input(input_data)
                
                if not is_valid:
                    if error_msg:
                        st.warning(f"🛡️ Input Safety: {error_msg}")
                    return AIMessage(content="I cannot process this request due to safety guidelines. Please rephrase your question.")
                
                input_data = processed_input
            
            elif isinstance(input_data, list):
                # Validate list of messages
                for i, message in enumerate(input_data):
                    if isinstance(message, HumanMessage):
                        is_valid, processed_input, error_msg = self.validation_service.validate_user_input(message.content)
                        
                        if not is_valid:
                            if error_msg:
                                st.warning(f"🛡️ Input Safety: {error_msg}")
                            return AIMessage(content="I cannot process this request due to safety guidelines. Please rephrase your question.")
                        
                        if processed_input != message.content:
                            input_data[i] = HumanMessage(content=processed_input)
            
            # Call original LLM
            result = self.llm.invoke(input_data, config, **kwargs)
            
            # Validate output
            if isinstance(result, AIMessage) and result.content:
                is_valid, processed_output, error_msg = self.validation_service.validate_llm_output(
                    result.content, self.usecase
                )
                
                if not is_valid:
                    if error_msg:
                        st.warning(f"🛡️ Output Safety: Response was filtered for safety")
                    result.content = processed_output
            
            return result
            
        except Exception as e:
            # Fall back to original LLM
            return self.llm.invoke(input_data, config, **kwargs)
    
    def bind_tools(self, tools, **kwargs):
        """Bind tools and return wrapped LLM"""
        bound_llm = self.llm.bind_tools(tools, **kwargs)
        return GuardrailsLLMWrapper(bound_llm, self.usecase)
    
    def __getattr__(self, name):
        """Delegate other attributes to the wrapped LLM"""
        return getattr(self.llm, name)


def create_guardrails_llm(llm: BaseLanguageModel, usecase: str = "general") -> BaseLanguageModel:
    """
    Create a Guardrails-wrapped LLM
    
    Args:
        llm: The original LLM to wrap
        usecase: The use case for appropriate validation rules
    
    Returns:
        Wrapped LLM with Guardrails validation
    """
    try:
        if validation_service.config.is_enabled():
            return GuardrailsLLMWrapper(llm, usecase)
        else:
            return llm
    except Exception:
        # If wrapping fails, return original LLM
        return llm