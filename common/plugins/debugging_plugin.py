from google.adk.plugins import BasePlugin
from google.adk.agents import BaseAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.llm_agent import LlmRequest
from google.adk.agents.llm_agent import LlmResponse
from google.adk.tools import BaseTool
from google.adk.tools.tool_context import ToolContext
from google.genai import types

from typing import Dict, Any, Optional
import datetime


class DebuggingPlugin(BasePlugin):
    def __init__(self):
        super().__init__(name="debugging_plugin")

    async def before_agent_callback(
        self, *, agent: BaseAgent, callback_context: CallbackContext
    ) -> None:
        """Log before agent execution."""
        print(f"\n[DEBUG] Agent '{agent.name}' starting")
        print(f"  Description: {agent.description}")
        print(f"  Agent type: {type(agent).__name__}")

    async def after_agent_callback(
        self, *, agent: BaseAgent, callback_context: CallbackContext
    ) -> Optional[types.Content]:
        """Log after agent execution."""
        print(f"\n[DEBUG] Agent '{agent.name}' completed")
        return None

    async def before_model_callback(
        self, *, callback_context: CallbackContext, llm_request: LlmRequest
    ) -> None:
        """Log before LLM request."""
        print(f"\n[DEBUG] LLM request starting")
        # print(f"  Model: {llm_request.model}")
        # print(f"  Agent: {callback_context.agent_name}")
        # if llm_request.config.system_instruction:
        #     instr = llm_request.config.system_instruction
        #     print(f"  System instruction: {instr}")

        # Inject environment context into system instruction
        now = datetime.datetime.now().astimezone()
        tz_abbr = now.strftime("%Z")  # e.g. IST
        utc_offset = now.strftime("%z")  # e.g. +0530
        utc_offset_fmt = f"UTC{utc_offset[:3]}:{utc_offset[3:]}"  # UTC+05:30

        env_context = (
            f"## Runtime Environment\n"
            f"- Date: {now.strftime('%Y-%m-%d')}\n"
            f"- Time: {now.strftime('%H:%M:%S')} {tz_abbr} ({utc_offset_fmt})"
        )
        llm_request.append_instructions([env_context])

    async def after_model_callback(
        self, *, callback_context: CallbackContext, llm_response: LlmResponse
    ) -> Optional[LlmResponse]:
        """Log after LLM response."""
        print(f"\n[DEBUG] LLM response received")
        return llm_response

    async def before_tool_callback(
        self, *, tool: BaseTool, tool_args: Dict[str, Any], tool_context: ToolContext
    ) -> Optional[dict]:
        """Log before tool execution."""
        print(f"\n[DEBUG] Tool '{tool.name}' calling")
        print(f"  Agent: {tool_context.agent_name}")
        print(f"  Args keys: {list(tool_args.keys()) if tool_args else 'none'}")
        return None

    async def after_tool_callback(
        self, *, tool: BaseTool, tool_args: Dict[str, Any], tool_context: ToolContext, result: dict
    ) -> Optional[dict]:
        """Log after tool execution."""
        print(f"\n[DEBUG] Tool '{tool.name}' completed")
        return None
