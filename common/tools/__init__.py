"""
Tools package for SDLC agent.
"""

from typing import Dict, Literal

from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams, StreamableHTTPConnectionParams
from google.adk.agents.context import Context
from google.adk.sessions.state import State

from mcp.client.stdio import StdioServerParameters
import os

from rpds import List
from typing import List

_AGENT_PLAYGROUND_BASE = "/home/bharath/workspace/agent-playground"


def _get_project_dir() -> str:
    explicit = os.environ.get("PROJECT_ROOT")
    if explicit:
        return explicit
    return os.path.join(_AGENT_PLAYGROUND_BASE, os.environ.get("PROJECT_NAME", "doll_shop"))


# Create memory MCP toolset for knowledge graph memory
memory_toolset = McpToolset(
    connection_params=StdioConnectionParams(
       timeout=120,
        server_params=StdioServerParameters(
            command='npx',
            args=["-y", "@modelcontextprotocol/server-memory"],
        ),
    ),
)

def get_documentation_files():
    """
    Returns contents of README.md and AGENTS.md files from the current directory.
    Returns a dictionary with file contents or error messages if files don't exist.
    """

    docs = {}
    files = ["README.md", "AGENTS.md", "progress.md", "CLAUDE.md"]

    for filename in files:
        filepath = os.path.join(_get_project_dir(), filename)
        try:
            with open(filepath, 'r') as f:
                docs[filename] = f.read()
        except FileNotFoundError:
            docs[filename] = f"File {filename} not found"
        except Exception as e:
            docs[filename] = f"Error reading {filename}: {str(e)}"

    return docs


tavily_toolset = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="https://mcp.tavily.com/mcp/?tavilyApiKey=" + os.environ.get("TAVILY_API_KEY", ""),
        timeout=120,
    ),
)


# --- Todo List Management Tools ---

import subprocess
import shlex
import uuid
from datetime import datetime, timezone
from typing import Optional

from common.tools.skills import list_skills, get_skill
