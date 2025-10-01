import streamlit as st
import os
from datetime import date

from langchain_core.messages import AIMessage, HumanMessage
from src.langgraphagenticai.ui.uiconfigfile import Config

class LoadStreamlitUI:
    def __init__(self):
        self.config = Config()
        self.user_controls = {}

    def initialize_session(self):
        return {
            "current_step": "requirements",
            "requirements": "",
            "user_stories": "",
            "po_feedback": "",
            "generated_code": "",
            "review_feedback": "",
            "decision": None
        }

    def render_requirements(self):
        st.markdown("## Requirements Submission")
        st.session_state.state["requirements"] = st.text_area(
            "Enter your requirements :",
            height=200,
            key="req_input"
        )
        if st.button("Submit Requirements", key="submit_req"):
            st.session_state.state["current_step"] = "generate_user_stories"
            st.session_state.IsSDLC = True

    def load_streamlit_ui(self):
        st.set_page_config(page_title= "🤖 " + self.config.get_page_title(), layout="wide")
        st.header("🤖 " + self.config.get_page_title())
        st.session_state.timeframe = ''
        st.session_state.IsFetchButtonClicked = False
        st.session_state.IsSDLC = False
        
        

        with st.sidebar:
            # Safety and Monitoring Status
            st.subheader("🛡️ Safety & Monitoring")
            
            # Guardrails status
            try:
                from src.langgraphagenticai.guardrail.validation_service import validation_service
                if validation_service.config.is_enabled():
                    st.success("🛡️ Guardrails: ON")
                    stats = validation_service.get_validation_stats()
                    if stats.get("total_guards", 0) > 0:
                        st.caption(f"Active guards: {stats['total_guards']}")
                else:
                    st.info("🛡️ Guardrails: OFF")
            except Exception:
                pass
            
            # Langfuse monitoring status - fail silently if monitoring unavailable
            try:
                from src.langgraphagenticai.monitoring.langfuse_integration import langfuse_manager
                if langfuse_manager.is_enabled():
                    st.success("📊 Monitoring: ON")
                    dashboard_url = langfuse_manager.get_dashboard_url()
                    st.markdown(f"[📈 View Dashboard]({dashboard_url})")
                else:
                    st.info("📊 Monitoring: OFF")
            except Exception:
                # If monitoring status can't be determined, don't show anything
                pass
            
            st.divider()
            
            # Get options from config
            llm_options = self.config.get_llm_options()
            usecase_options = self.config.get_usecase_options()

            # LLM selection
            self.user_controls["selected_llm"] = st.selectbox("Select LLM", llm_options)

            if self.user_controls["selected_llm"] == 'Groq':
                # Model selection
                model_options = self.config.get_groq_model_options()
                self.user_controls["selected_groq_model"] = st.selectbox("Select Model", model_options)
                # API key input
                self.user_controls["GROQ_API_KEY"] = st.session_state["GROQ_API_KEY"] = st.text_input("API Key",
                                                                                                      type="password")
                # Validate API key
                if not self.user_controls["GROQ_API_KEY"]:
                    st.warning("⚠️ Please enter your GROQ API key to proceed. Don't have? refer : https://console.groq.com/keys ")
                   
            
            # Use case selection
            self.user_controls["selected_usecase"] = st.selectbox("Select Usecases", usecase_options)

            if self.user_controls["selected_usecase"] =="Chatbot with Tool" or self.user_controls["selected_usecase"] =="AI News" :
                # API key input
                os.environ["TAVILY_API_KEY"] = self.user_controls["TAVILY_API_KEY"] = st.session_state["TAVILY_API_KEY"] = st.text_input("TAVILY API KEY",
                                                                                                      type="password")
                # Validate API key
                if not self.user_controls["TAVILY_API_KEY"]:
                    st.warning("⚠️ Please enter your TAVILY_API_KEY key to proceed. Don't have? refer : https://app.tavily.com/home")

                elif self.user_controls['selected_usecase']=="AI News":
                    st.subheader("📰 AI News Explorer ")
                    
                    with st.sidebar:
                        time_frame = st.selectbox(
                            "📅 Select Time Frame",
                            ["Daily", "Weekly", "Monthly"],
                            index=0
                        )
                    
                    if st.button("🔍 Fetch Latest AI News", use_container_width=True):
                        st.session_state.IsFetchButtonClicked = True
                        st.session_state.timeframe = time_frame
                    else :
                        st.session_state.IsFetchButtonClicked = False
            
            elif self.user_controls["selected_usecase"] == "MCP Chatbot":
                st.subheader("🔧 MCP Configuration")
                
                # Sample config button
                if st.button("📋 Load Sample Config"):
                    from src.langgraphagenticai.tools.mcp_tools import get_sample_mcp_config
                    st.session_state.mcp_config_text = get_sample_mcp_config()
                
                # MCP Config input
                mcp_config_text = st.text_area(
                    "MCP Configuration JSON:",
                    value=st.session_state.get("mcp_config_text", ""),
                    height=300,
                    help="Paste your MCP server configuration JSON here"
                )
                
                if mcp_config_text:
                    st.session_state.mcp_config_text = mcp_config_text
                    
                    # Validate config
                    from src.langgraphagenticai.tools.mcp_tools import validate_mcp_config
                    validated_config = validate_mcp_config(mcp_config_text)
                    
                    if validated_config:
                        self.user_controls["mcp_config"] = validated_config
                        st.success("✅ MCP configuration is valid!")
                        
                        # Show configured servers
                        servers = validated_config.get("mcpServers", {})
                        enabled_servers = [name for name, config in servers.items() if not config.get("disabled", False)]
                        
                        if enabled_servers:
                            st.info(f"🚀 Enabled MCP servers: {', '.join(enabled_servers)}")
                        else:
                            st.warning("⚠️ No enabled MCP servers found in configuration")
                    else:
                        st.error("❌ Invalid MCP configuration")
                else:
                    st.info("💡 Please provide MCP configuration to use MCP tools")
            
            if "state" not in st.session_state:
                st.session_state.state = self.initialize_session()

            # self.render_requirements()
            
        return self.user_controls