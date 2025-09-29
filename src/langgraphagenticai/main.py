import streamlit as st
import json
import os
from src.langgraphagenticai.ui.streamlitui.loadui import LoadStreamlitUI
from src.langgraphagenticai.llms.groqllm import GroqLLM
from src.langgraphagenticai.graph.graph_builder import GraphBuilder
from src.langgraphagenticai.ui.streamlitui.display_result import DisplayResultStremlit
# Import monitoring - but don't fail if it's not available
try:
    from src.langgraphagenticai.monitoring.langfuse_integration import langfuse_manager
except ImportError:
    langfuse_manager = None


# Main function START
def load_langgraph_agenticai_app():
    # Load UI
    ui = LoadStreamlitUI()
    user_input = ui.load_streamlit_ui()

    if not user_input:
        st.error("Error: Failed to load user input from the UI")

    # Text input for user message
    if st.session_state.IsFetchButtonClicked:
        user_message = st.session_state.timeframe
    # elif st.session_state.IsSDLC:
    #     user_message = st.session_state.state
    else:
        user_message = st.chat_input("Enter your message :")

    if user_message:
        try:
            # Get usecase first
            usecase = user_input.get("selected_usecase", "general")
            
            # Configure LLM with usecase for appropriate guardrails
            obj_llm_config = GroqLLM(user_controls_input=user_input)
            model = obj_llm_config.get_llm_model(usecase=usecase)

            if not model:
                st.error("Error: LLM model could not be initialized")
                return

            # Validate usecase
            if not usecase:
                st.error("Error: no usecase selected")
                return

            # Set TAVILY API key if needed for tool-based usecases
            if usecase in ["Chatbot with Tool", "AI News"]:
                tavily_key = user_input.get("TAVILY_API_KEY")
                if tavily_key:
                    os.environ["TAVILY_API_KEY"] = tavily_key
                else:
                    st.error("TAVILY API key is required for this usecase")
                    return

            # Graph Builder
            graph_builder = GraphBuilder(model)

            try:
                # Pass MCP config if it's an MCP usecase
                if usecase == "MCP Chatbot":
                    mcp_config = user_input.get("mcp_config")
                    if not mcp_config:
                        st.error("MCP configuration is required for MCP Chatbot")
                        return
                    graph = graph_builder.setup_graph(usecase=usecase, mcp_config=mcp_config)
                else:
                    graph = graph_builder.setup_graph(usecase=usecase)
                DisplayResultStremlit(
                    usecase, graph, user_message
                ).display_result_on_ui()
            except Exception as e:
                st.error(f"Error: Graph setup failed - {e}")
        except Exception as e:
            raise ValueError(f"Error occur with exception : {e}")
