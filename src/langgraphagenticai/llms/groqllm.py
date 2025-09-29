import os
import streamlit as st
from langchain_groq import ChatGroq
from src.langgraphagenticai.monitoring.langfuse_integration import create_monitored_llm, get_langfuse_callbacks
from src.langgraphagenticai.guardrails.llm_wrapper import create_guardrails_llm


class GroqLLM:
    def __init__(self, user_controls_input):
        self.user_controls_input = user_controls_input

    def get_llm_model(self, usecase: str = "general"):
        try:
            groq_api_key = self.user_controls_input.get("GROQ_API_KEY")
            selected_groq_model = self.user_controls_input.get("selected_groq_model")

            if not groq_api_key or not selected_groq_model:
                st.error("Please enter the GROQ API key and select a model")
                return None

            # Create base LLM first
            llm = ChatGroq(
                api_key=groq_api_key, 
                model=selected_groq_model
            )
            
            # Add Guardrails protection
            try:
                llm = create_guardrails_llm(llm, usecase)
            except Exception:
                # If Guardrails fails, continue without it
                pass
            
            # Try to add monitoring, but don't fail if it doesn't work
            try:
                callbacks = get_langfuse_callbacks()
                if callbacks:
                    llm.callbacks = callbacks
                
                # Wrap with Langfuse monitoring
                monitored_llm = create_monitored_llm(llm)
                return monitored_llm
            except Exception:
                # If monitoring fails, return the LLM (possibly with Guardrails)
                return llm
        except Exception as e:
            st.error(f"Error initializing ChatGroq: {str(e)}")
            print(str(e))
            return None

        