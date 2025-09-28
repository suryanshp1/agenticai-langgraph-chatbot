"""
MCP Tools Integration
Handles MCP server connections and tool creation for LangGraph
"""
import json
import asyncio
import subprocess
from typing import Dict, List, Any, Optional
import streamlit as st
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
import tempfile
import os


class MCPTool(BaseTool):
    """A LangChain tool that wraps MCP functionality"""
    name: str = Field(...)
    description: str = Field(...)
    mcp_command: str = Field(...)
    mcp_args: List[str] = Field(default_factory=list)
    mcp_env: Dict[str, str] = Field(default_factory=dict)
    
    def _run(self, query: str) -> str:
        """Execute the MCP tool"""
        try:
            # Set up environment
            env = os.environ.copy()
            env.update(self.mcp_env)
            
            # Create a simple input for the MCP server
            input_data = {
                "method": "tools/call",
                "params": {
                    "name": self.name,
                    "arguments": {"query": query}
                }
            }
            
            # Run the MCP server command
            result = subprocess.run(
                [self.mcp_command] + self.mcp_args,
                input=json.dumps(input_data),
                capture_output=True,
                text=True,
                env=env,
                timeout=30
            )
            
            if result.returncode == 0:
                return result.stdout
            else:
                return f"Error: {result.stderr}"
                
        except Exception as e:
            return f"Error executing MCP tool: {str(e)}"


def create_mcp_tools_from_config(mcp_config: Dict[str, Any]) -> List[MCPTool]:
    """Create MCP tools from configuration"""
    tools = []
    
    try:
        mcp_servers = mcp_config.get("mcpServers", {})
        
        for server_name, server_config in mcp_servers.items():
            if server_config.get("disabled", False):
                continue
                
            # Create a generic tool for each MCP server
            tool = MCPTool(
                name=f"mcp_{server_name}",
                description=f"MCP tool for {server_name} server - can handle various queries and operations",
                mcp_command=server_config.get("command", "uvx"),
                mcp_args=server_config.get("args", []),
                mcp_env=server_config.get("env", {})
            )
            tools.append(tool)
            
    except Exception as e:
        st.error(f"Error creating MCP tools: {e}")
    
    return tools


def validate_mcp_config(config_text: str) -> Optional[Dict[str, Any]]:
    """Validate MCP configuration JSON"""
    try:
        config = json.loads(config_text)
        
        # Basic validation
        if "mcpServers" not in config:
            st.error("MCP config must contain 'mcpServers' key")
            return None
            
        # Validate each server config
        for server_name, server_config in config["mcpServers"].items():
            if "command" not in server_config:
                st.error(f"Server '{server_name}' must have 'command' field")
                return None
                
        return config
        
    except json.JSONDecodeError as e:
        st.error(f"Invalid JSON: {e}")
        return None
    except Exception as e:
        st.error(f"Error validating config: {e}")
        return None


def get_sample_mcp_config() -> str:
    """Get a sample MCP configuration"""
    return json.dumps({
        "mcpServers": {
            "filesystem": {
                "command": "uvx",
                "args": ["mcp-server-filesystem", "/tmp"],
                "disabled": False,
                "autoApprove": [],
                "disabledTools": []
            },
            "brave-search": {
                "command": "uvx",
                "args": ["mcp-server-brave-search"],
                "env": {
                    "BRAVE_API_KEY": "your_brave_api_key_here"
                },
                "disabled": True,
                "autoApprove": [],
                "disabledTools": []
            },
            "sqlite": {
                "command": "uvx",
                "args": ["mcp-server-sqlite", "--db-path", "/tmp/test.db"],
                "disabled": False,
                "autoApprove": [],
                "disabledTools": []
            }
        }
    }, indent=2)