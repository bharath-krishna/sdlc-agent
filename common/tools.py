import os
from typing import Literal

from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams, StreamableHTTPConnectionParams
from mcp.client.stdio import StdioServerParameters

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


filesystem_toolset = McpToolset(
    connection_params=StdioConnectionParams(
       timeout=120,
        server_params=StdioServerParameters(
            command='npx',
            args=["-y", "@modelcontextprotocol/server-filesystem", _get_project_dir()],
            cwd=_get_project_dir(),
        ),
    ),
)

readonly_filesystem_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        timeout=120,
        server_params=StdioServerParameters(
            command='npx',
            args=["-y", "@modelcontextprotocol/server-filesystem", _get_project_dir()],
            cwd=_get_project_dir(),
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
                args=["-y", "@modelcontextprotocol/server-filesystem", _get_project_dir()],
                cwd=_get_project_dir(),
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


def run_shell_command(command: str):
    """
    A simple tool to execute bash commands in the project directory.
    args:
        command: The bash command to execute.
    returns:
        output: The output of the command or error message if it fails.
    """
    project_dir = _get_project_dir()
    print(f"  [Tool Call] run_shell_command executing command: {command}")
    try:
        # Wrap in a subshell pinned to project_dir so `cd` inside the command can't escape it.
        safe_command = f"cd {shlex.quote(project_dir)} && ( {command} )"
        result = subprocess.check_output(safe_command, shell=True, text=True, stderr=subprocess.STDOUT)
        return {"output": result}
    except subprocess.CalledProcessError as e:
        return {"error": str(e), "output": e.output}

TODOS_STATE_KEY = "sdlc_todos"


def _get_now_iso8601() -> str:
    """Return current time in ISO8601 format."""
    return datetime.now(timezone.utc).isoformat()


def _ensure_todos_in_state(state: dict) -> list:
    """Ensure todos list exists in state, initialize if missing."""
    if TODOS_STATE_KEY not in state:
        state[TODOS_STATE_KEY] = []
    return state[TODOS_STATE_KEY]


def get_todos_from_state(state: dict) -> list:
    """
    Helper function to read todos from any state dict (for plugins/callbacks).

    Args:
        state: The state dict (e.g., callback_context.state)

    Returns:
        List of todo dicts
    """
    return _ensure_todos_in_state(state)


def set_todos_in_state(state: dict, todos: list) -> None:
    """
    Helper function to write todos into any state dict (for plugins/callbacks).

    Args:
        state: The state dict (e.g., callback_context.state)
        todos: List of todo dicts
    """
    state[TODOS_STATE_KEY] = todos


def get_todos(tool_context):
    """
    Get all todos from the session.

    Returns:
        Dictionary with list of todos
    """
    todos = _ensure_todos_in_state(tool_context.state)
    return {"todos": todos}


def add_todo(title: str, description: str = "", priority: str = "medium", tool_context=None):
    """
    Add a new todo to the list.

    Args:
        title: Short title of the todo
        description: Longer description (optional)
        priority: Priority level - "low", "medium", or "high" (default: "medium")
        tool_context: Injected by framework

    Returns:
        Dictionary with the created todo
    """
    if not title:
        return {"error": "title is required"}

    if priority not in ("low", "medium", "high"):
        return {"error": f"priority must be 'low', 'medium', or 'high', got '{priority}'"}

    todos = _ensure_todos_in_state(tool_context.state)

    now = _get_now_iso8601()
    todo = {
        "id": uuid.uuid4().hex,
        "title": title,
        "description": description,
        "status": "pending",
        "priority": priority,
        "created_at": now,
        "updated_at": now,
    }

    todos.append(todo)
    return {"todo": todo}


def update_todo(
    todo_id: str,
    tool_context=None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
):
    """
    Update an existing todo by id.

    Args:
        todo_id: The id of the todo to update
        tool_context: Injected by framework
        title: New title (optional)
        description: New description (optional)
        status: New status - "pending", "in_progress", or "done" (optional)
        priority: New priority - "low", "medium", or "high" (optional)

    Returns:
        Dictionary with updated todo or error
    """
    if status and status not in ("pending", "in_progress", "done"):
        return {"error": f"status must be 'pending', 'in_progress', or 'done', got '{status}'"}

    if priority and priority not in ("low", "medium", "high"):
        return {"error": f"priority must be 'low', 'medium', or 'high', got '{priority}'"}

    todos = _ensure_todos_in_state(tool_context.state)

    # Find the todo
    todo_idx = None
    for i, t in enumerate(todos):
        if t["id"] == todo_id:
            todo_idx = i
            break

    if todo_idx is None:
        return {"error": f"todo with id '{todo_id}' not found"}

    todo = todos[todo_idx]

    # Update fields
    if title is not None:
        todo["title"] = title
    if description is not None:
        todo["description"] = description
    if status is not None:
        todo["status"] = status
    if priority is not None:
        todo["priority"] = priority

    todo["updated_at"] = _get_now_iso8601()

    return {"todo": todo}


def remove_todo(todo_id: str, tool_context=None):
    """
    Remove a todo by id.

    Args:
        todo_id: The id of the todo to remove
        tool_context: Injected by framework

    Returns:
        Dictionary with removed id or error
    """
    todos = _ensure_todos_in_state(tool_context.state)

    # Find and remove
    for i, t in enumerate(todos):
        if t["id"] == todo_id:
            todos.pop(i)
            return {"removed": todo_id}

    return {"error": f"todo with id '{todo_id}' not found"}


def clear_todos(tool_context=None):
    """
    Clear all todos from the session.

    Args:
        tool_context: Injected by framework

    Returns:
        Dictionary with count of cleared todos
    """
    todos = _ensure_todos_in_state(tool_context.state)
    count = len(todos)
    tool_context.state[TODOS_STATE_KEY] = []
    return {"cleared": count}
