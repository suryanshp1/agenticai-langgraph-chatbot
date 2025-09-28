"""
MCP Client Manager
Handles connections to MCP servers and tool management
"""
import asyncio
import subprocess
from typing import Dict, List, Any, Optional
import streamlit as st
from langchain_mcp_adapters import MCPToolkit
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from .mcp_config import MCPConfig


class MCPClientManager:
    def __init__(self):
        self.config = MCPConfig()
        self.active_sessions: Dict[str, ClientSession] = {}
        self.toolkits: Dict[str, MCPToolkit] = {}

    async def connect_to_server(self, server_name: str, server_config: Dict[str, Any]) -> Optional[MCPToolkit]:
        """Connect to an MCP server and return its toolkit"""
        try:
            # Create server parameters
            server_params = StdioServerParameters(
                command=server_config["command"],
                args=server_config.get("args", []),
                env=server_config.get("env", {})
            )
            
            # Create stdio client
            stdio_transport = await stdio_client(server_params)
            
            # Create session
            session = ClientSession(stdio_transport[0], stdio_transport[1])
            
            # Initialize session
            await session.initialize()
            
            # Store session
            self.active_sessions[server_name] = session
            
            # Create toolkit
            toolkit = MCPToolkit(session=session)
            self.toolkits[server_name] = toolkit
            
            st.success(f"✅ Connected to MCP server: {server_name}")
            return toolkit
            
        except Exception as e:
            st.error(f"❌ Failed to connect to MCP server {server_name}: {e}")
            return None

    async def connect_all_servers(self) -> Dict[str, MCPToolkit]:
        """Connect to all enabled MCP servers"""
        enabled_servers = self.config.get_enabled_servers()
        connected_toolkits = {}
        
        for server_name, server_config in enabled_servers.items():
            toolkit = await self.connect_to_server(server_name, server_config)
            if toolkit:
                connected_toolkits[server_name] = toolkit
        
        return connected_toolkits

    def get_all_tools(self) -> List[Any]:
        """Get all tools from all connected MCP servers"""
        all_tools = []
        
        for server_name, toolkit in self.toolkits.items():
            try:
                server_config = self.config.get_server_config(server_name)
                disabled_tools = server_config.get("disabledTools", [])
                
                # Get tools from toolkit
                tools = toolkit.get_tools()
                
                # Filter out disabled tools
                enabled_tools = [
                    tool for tool in tools 
                    if tool.name not in disabled_tools
                ]
                
                all_tools.extend(enabled_tools)
                st.info(f"📦 Loaded {len(enabled_tools)} tools from {server_name}")
                
            except Exception as e:
                st.warning(f"⚠️ Error getting tools from {server_name}: {e}")
        
        return all_tools

    async def disconnect_all(self):
        """Disconnect from all MCP servers"""
        for server_name, session in self.active_sessions.items():
            try:
                await session.close()
                st.info(f"🔌 Disconnected from {server_name}")
            except Exception as e:
                st.warning(f"⚠️ Error disconnecting from {server_name}: {e}")
        
        self.active_sessions.clear()
        self.toolkits.clear()

    def is_server_available(self, server_name: str) -> bool:
        """Check if a server is available and responding"""
        server_config = self.config.get_server_config(server_name)
        if not server_config:
            return False
        
        try:
            # Try to run the command to see if it's available
            result = subprocess.run(
                [server_config["command"], "--help"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False