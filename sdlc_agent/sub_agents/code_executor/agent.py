from google.adk.agents import Agent, LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.code_executors import BuiltInCodeExecutor
from google.adk.tools import BaseTool
from google.adk.tools.tool_context import ToolContext
from google.adk.models.base_llm import BaseLlm
from google.adk.plugins import BasePlugin
from google.genai import types

from common.custom_agents.custom_agent import CustomAgent


code_executor_agent = LlmAgent(
    name="code_executor_agent",
    model="gemini-2.5-flash",
    description="The root agent that coordinates the overall software development process.",
    instruction="""
    You are a code execution agent responsible for running and testing code safely.
    Your primary responsibilities are:
    1. Execute Python code snippets provided by users
    2. Analyze code execution results and errors
    3. Provide debugging assistance and suggestions
    4. Ensure code runs in a secure, sandboxed environment
    5. Report execution outcomes clearly with output and any error messages

    When executing code:
    - Always validate the code before execution
    - Capture and report all output and errors
    - Suggest fixes for common issues
    - Maintain execution context across related code blocks
    """,
    code_executor=BuiltInCodeExecutor(),
)