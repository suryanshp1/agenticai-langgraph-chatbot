"""
MCP Configuration Management
Handles loading and managing MCP server configurations
"""

import json
import os
from typing import Dict, List, Any, Optional
import streamlit as st


class MCPConfig:
    def __init__(self):
        self.workspace_config_path = ".kiro/settings/mcp.json"
        self.user_config_path = os.path.expanduser("~/.kiro/settings/mcp.json")
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load MCP configuration from workspace and user level configs"""
        config = {"mcpServers": {}}

        # Load user-level config first
        user_config = self._load_config_file(self.user_config_path)
        if user_config and "mcpServers" in user_config:
            config["mcpServers"].update(user_config["mcpServers"])

        # Load workspace-level config (takes precedence)
        workspace_config = self._load_config_file(self.workspace_config_path)
        if workspace_config and "mcpServers" in workspace_config:
            config["mcpServers"].update(workspace_config["mcpServers"])

        return config

    def _load_config_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Load a single MCP config file"""
        try:
            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    return json.load(f)
        except Exception as e:
            st.warning(f"Error loading MCP config from {file_path}: {e}")
        return None

    def get_enabled_servers(self) -> Dict[str, Dict[str, Any]]:
        """Get all enabled MCP servers"""
        enabled_servers = {}
        for server_name, server_config in self.config.get("mcpServers", {}).items():
            if not server_config.get("disabled", False):
                enabled_servers[server_name] = server_config
        return enabled_servers

    def get_server_config(self, server_name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific server"""
        return self.config.get("mcpServers", {}).get(server_name)

    def create_default_config(self):
        """Create a default MCP configuration file"""
        default_config = {
            "mcpServers": {
                "filesystem": {
                    "command": "uvx",
                    "args": ["mcp-server-filesystem", "/tmp"],
                    "disabled": False,
                    "autoApprove": [],
                    "disabledTools": [],
                },
                "brave-search": {
                    "command": "uvx",
                    "args": ["mcp-server-brave-search"],
                    "env": {"BRAVE_API_KEY": "your_brave_api_key_here"},
                    "disabled": True,
                    "autoApprove": [],
                    "disabledTools": [],
                },
            }
        }

        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.workspace_config_path), exist_ok=True)

        # Write default config
        with open(self.workspace_config_path, "w") as f:
            json.dump(default_config, f, indent=2)

        return default_config
