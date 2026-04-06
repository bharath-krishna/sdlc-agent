from google.adk.plugins import BasePlugin
from google.adk.agents import BaseAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.llm_agent import LlmRequest
from google.adk.agents.llm_agent import LlmResponse
from google.adk.tools import BaseTool
from google.adk.tools.tool_context import ToolContext
from google.genai import types

from typing import Dict, Any, Optional


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
        print(f"  Model: {llm_request.model}")
        print(f"  Agent: {callback_context.agent_name}")
        if llm_request.config.system_instruction:
            instr = llm_request.config.system_instruction
            instr_text = instr if isinstance(instr, str) else getattr(instr, 'text', str(instr)[:100])
            print(f"  System instruction (first 100 chars): {str(instr_text)[:100]}")

    async def after_model_callback(
        self, *, callback_context: CallbackContext, llm_response: LlmResponse
    ) -> Optional[LlmResponse]:
        """Log after LLM response."""
        print(f"\n[DEBUG] LLM response received")
        if llm_response.usage_metadata:
            print(f"  Input tokens: {llm_response.usage_metadata.input_token_count}")
            print(f"  Output tokens: {llm_response.usage_metadata.output_token_count}")
            print(f"  Total tokens: {llm_response.usage_metadata.total_token_count}")
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
        if result:
            result_keys = list(result.keys()) if isinstance(result, dict) else 'not a dict'
            print(f"  Result keys: {result_keys}")
        return None
