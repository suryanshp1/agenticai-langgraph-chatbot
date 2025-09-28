from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.prebuilt import ToolNode
import os

def get_tools():
    """
    Return the list of tools to be used in the chatbot
    """
    # Check if TAVILY_API_KEY is set
    if not os.getenv("TAVILY_API_KEY"):
        raise ValueError("TAVILY_API_KEY environment variable is not set")
    
    tool = TavilySearchResults(max_results=2)
    return [tool]

def create_tool_node(tools):
    """
    Creates and return tool node for the graph
    """
    return ToolNode(tools=tools)