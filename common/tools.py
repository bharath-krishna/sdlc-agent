from typing import Literal

from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams, StreamableHTTPConnectionParams
from mcp.client.stdio import StdioServerParameters
import os

from rpds import List
from typing import List


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


filesystem_toolset = McpToolset(
    connection_params=StdioConnectionParams(
       timeout=120,
        server_params=StdioServerParameters(
            command='npx',
            args=["-y", "@modelcontextprotocol/server-filesystem", "/home/bharath/workspace/sdlc-agent/doll_shop"],
        ),
    ),
)

readonly_filesystem_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        timeout=120,
        server_params=StdioServerParameters(
            command='npx',
            args=["-y", "@modelcontextprotocol/server-filesystem", "/home/bharath/workspace/sdlc-agent/doll_shop"],
        ),
    ),
    tool_filter=[
        "read_text_file",
        "read_media_file",
        "read_multiple_files",
        "list_directory",
        "list_directory_with_sizes",
        "directory_tree",
        "search_files",
        "get_file_info",
        "list_allowed_directories",
    ]
)

filesystem_tools = [
    "read_text_file",
    "read_media_file",
    "read_multiple_files",
    "list_directory",
    "list_directory_with_sizes",
    "directory_tree",
    "search_files",
    "get_file_info",
    "list_allowed_directories",
]

def get_filesystem_toolset(tool_filter: List[str] = filesystem_tools) -> McpToolset:
    return McpToolset(
        connection_params=StdioConnectionParams(
            timeout=120,
            server_params=StdioServerParameters(
                command='npx',
                args=["-y", "@modelcontextprotocol/server-filesystem", "/home/bharath/workspace/sdlc-agent/doll_shop"],
            ),
        ),
        tool_filter=tool_filter,
    )

def get_documentation_files():
    """
    Returns contents of README.md and AGENTS.md files from the current directory.
    Returns a dictionary with file contents or error messages if files don't exist.
    """
    
    docs = {}
    files = ["README.md", "AGENTS.md", "progress.md", "CLAUDE.md"]
    
    for filename in files:
        filepath = os.path.join("/home/bharath/workspace/sdlc-agent/doll_shop", filename)
        try:
            with open(filepath, 'r') as f:
                docs[filename] = f.read()
        except FileNotFoundError:
            docs[filename] = f"File {filename} not found"
        except Exception as e:
            docs[filename] = f"Error reading {filename}: {str(e)}"
    
    return docs