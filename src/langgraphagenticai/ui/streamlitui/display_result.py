import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
import json

class DisplayResultStremlit:
    def __init__(self, usecase, graph, user_message):
        self.usecase = usecase
        self.graph = graph
        self.user_message = user_message

    def display_result_on_ui(self):
        usecase = self.usecase
        graph = self.graph
        user_message = self.user_message
        if usecase == "Basic Chatbot":
            for event in graph.stream({"messages": ("user", user_message)}):
                print(event.values())
                for value in event.values():
                    print(value["messages"])
                    with st.chat_message("user"):
                        st.write(user_message)
                    with st.chat_message("assisstant"):
                        st.write(value["messages"].content)

        elif usecase == "Chatbot with Tool" or usecase == "AI News":
            # Prepare state and invoke the graph
            initial_state = {"messages": [HumanMessage(content=user_message)]}
            
            # Display user message
            with st.chat_message("user"):
                st.write(user_message)
            
            # Stream the graph execution
            for event in graph.stream(initial_state):
                for node_name, node_output in event.items():
                    if "messages" in node_output:
                        messages = node_output["messages"]
                        if not isinstance(messages, list):
                            messages = [messages]
                        
                        for message in messages:
                            if isinstance(message, ToolMessage):
                                with st.chat_message("assistant"):
                                    st.write("🔍 **Tool Search Results:**")
                                    st.write(message.content)
                            elif isinstance(message, AIMessage):
                                if message.tool_calls:
                                    with st.chat_message("assistant"):
                                        st.write("🔧 **Calling search tool...**")
                                        for tool_call in message.tool_calls:
                                            st.write(f"Searching for: {tool_call['args'].get('query', 'N/A')}")
                                else:
                                    with st.chat_message("assistant"):
                                        st.write(message.content)
                