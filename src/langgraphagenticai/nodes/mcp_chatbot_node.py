"""
MCP Chatbot Node
Handles chatbot logic with MCP tools integration
"""
from src.langgraphagenticai.state.state import State
from typing import List, Any


class MCPChatbotNode:
    """
    Chatbot logic enhanced with MCP tools integration
    """
    def __init__(self, model):
        self.llm = model

    def create_chatbot(self, tools: List[Any]):
        """
        Returns a chatbot node function with MCP tools
        """
        llm_with_tools = self.llm.bind_tools(tools)

        def chatbot_node(state: State):
            """
            Chatbot logic for processing the input state and returning a response
            """
            return {"messages": [llm_with_tools.invoke(state["messages"])]}

        return chatbot_node