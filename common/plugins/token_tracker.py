from google.adk.plugins import BasePlugin
from google.adk.agents import BaseAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.llm_agent import LlmRequest
from google.adk.agents.llm_agent import LlmResponse
from google.adk.tools import BaseTool
from google.adk.tools.tool_context import ToolContext
from google.genai import types

from typing import Dict, Any
from typing import Optional


class TokenTracker(BasePlugin):
    def __init__(self):
        super().__init__(name="tokern_tracker")
        self.total_tokens: int = 0
        self.agent_count: int = 0
        self.tool_count: int = 0
        self.llm_request_count: int = 0

    async def before_agent_callback(
        self, *, agent: BaseAgent, callback_context: CallbackContext
    ) -> None:
        """Count agent runs."""
        print(f"[Plugin] Agent '{agent.name}' is about to run.")
        print(f"callback_context: {callback_context}")
        # self.total_tokens += callback_context.
        self.agent_count += 1
        print(f"[Plugin] Agent run count: {self.agent_count}")

    async def after_agent_callback(
            self, *, agent: BaseAgent, callback_context: CallbackContext
  ) -> Optional[types.Content]:
        print(f"[Plugin] Agent '{agent.name}' has finished running.")
        print(f"callback_context: {callback_context}")
        return

    async def before_model_callback(
        self, *, callback_context: CallbackContext, llm_request: LlmRequest
    ) -> None:
        """Count LLM requests."""
        self.llm_request_count += 1
        print(f"[Plugin] LLM request count: {self.llm_request_count}")
    
    async def after_model_callback(
        self, callback_context: CallbackContext, llm_response: LlmResponse
    ) -> Optional[LlmResponse]:
        """Count tokens in LLM responses."""
        if llm_response.usage_metadata:
            self.total_tokens += llm_response.usage_metadata.total_token_count
            if self.total_tokens > 217942:
                print(f"[Plugin] Warning: Total tokens used ({self.total_tokens}) has exceeded the threshold!")
                # TODO: Add logic to handle token limit breach, e.g., compact the conversation, alert the user, etc.
            print(f"[Plugin] Total tokens used: {self.total_tokens}")

        return llm_response

    async def before_tool_callback(
        self, *, tool: BaseTool, tool_args: Dict[str, Any], tool_context: ToolContext
    ) -> Optional[dict]:
        """Count tool calls."""
        self.tool_count += 1
        print(f"[Plugin] Tool '{tool.name}' is about to be called.")
        print(f"tool_context: {tool_context}")
        print(f"[Plugin] Tool call count: {self.tool_count}")

        # print(f"[Plugin] Preventing tool '{tool.name}' from being called.")
        # tool_context._invocation_context.end_invocation = True
        return

    async def after_tool_callback(
            self, *, tool: BaseTool, tool_args: Dict[str, Any], tool_context: ToolContext, result: dict
    ) -> Optional[dict]:
        print(f"[Plugin] Tool '{tool.name}' has been called.")
        print(f"tool_context: {tool_context}")
        print(f"result: {result}")
