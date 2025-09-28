from langgraph.graph import StateGraph, END, START, MessagesState
from langgraph.prebuilt import tools_condition, ToolNode
from langchain_core.prompts import ChatPromptTemplate
from src.langgraphagenticai.state.state import State
from src.langgraphagenticai.nodes.basic_chatbot_node import BasicChatbotNode
from src.langgraphagenticai.nodes.chatbot_with_tool_node import ChatbotWithToolNode
from src.langgraphagenticai.tools.search_tool import get_tools, create_tool_node
import datetime


class GraphBuilder:
    def __init__(self, model):
        self.llm = model

    def basic_chatbot_build_graph(self):
        graph_builder = StateGraph(State)
        self.basic_chatbot_node = BasicChatbotNode(self.llm)
        graph_builder.add_node("chatbot", self.basic_chatbot_node.process)
        graph_builder.add_edge(START, "chatbot")
        graph_builder.add_edge("chatbot", END)
        return graph_builder

    def chatbot_with_tools_build_graph(self):
        graph_builder = StateGraph(State)

        # define tools and toolnode
        tools = get_tools()
        tool_node = create_tool_node(tools=tools)

        # define llm
        llm = self.llm

        # define chatbot node
        obj_chatbot_with_node = ChatbotWithToolNode(llm)
        chatbot_node = obj_chatbot_with_node.create_chatbot(tools=tools)

        # Add nodes
        graph_builder.add_node("chatbot", chatbot_node)
        graph_builder.add_node("tools", tool_node)

        # Define conditional and direct edges
        graph_builder.add_edge(START, "chatbot")
        graph_builder.add_conditional_edges("chatbot", tools_condition)
        graph_builder.add_edge("tools", "chatbot")

        return graph_builder

    def setup_graph(self, usecase: str):
        if usecase == "Basic Chatbot":
            graph_builder = self.basic_chatbot_build_graph()
        elif usecase == "Chatbot with Tool":
            graph_builder = self.chatbot_with_tools_build_graph()
        elif usecase == "AI News":
            graph_builder = (
                self.chatbot_with_tools_build_graph()
            )  # AI News also uses tools
        else:
            raise ValueError(f"Unknown usecase: {usecase}")

        return graph_builder.compile()
