from google.adk.plugins import BasePlugin
from google.adk.agents import BaseAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.llm_agent import LlmRequest
from google.adk.agents.llm_agent import LlmResponse
from google.adk.tools import BaseTool
from google.adk.tools.tool_context import ToolContext
from google.adk.apps.llm_event_summarizer import LlmEventSummarizer
from google.adk.models.base_llm import BaseLlm
from google.genai import types

from typing import Dict, Any
from typing import Optional


class TokenTracker(BasePlugin):
    def __init__(
        self,
        token_threshold: int = 10000,
        summarization_llm: Optional[BaseLlm] = None,
    ):
        super().__init__(name="token_tracker")
        self.total_tokens: int = 0
        self.agent_count: int = 0
        self.tool_count: int = 0
        self.llm_request_count: int = 0
        self.token_threshold = token_threshold
        self._summarizer = LlmEventSummarizer(llm=summarization_llm) if summarization_llm else None

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
        self, *, callback_context: CallbackContext, llm_response: LlmResponse
    ) -> Optional[LlmResponse]:
        """Count tokens in LLM responses."""
        if llm_response.usage_metadata:
            self.total_tokens = llm_response.usage_metadata.total_token_count
            if self.total_tokens > self.token_threshold:
                print(f"[Plugin] Warning: Total tokens used ({self.total_tokens}) has exceeded the threshold! ({self.token_threshold})")
                # if self._summarizer is not None:
                #     session = callback_context._invocation_context.session
                #     session_service = callback_context._invocation_context.session_service
                #     compaction_event = await self._summarizer.maybe_summarize_events(
                #         events=session.events
                #     )
                #     if compaction_event is not None:
                #         await session_service.append_event(session, compaction_event)
                #         self.total_tokens = 0
                #         print("[Plugin] Conversation summarized and compacted successfully.")
            print(f"[Plugin] Total tokens used: {self.total_tokens}")

        return llm_response

    async def before_tool_callback(
        self, *, tool: BaseTool, tool_args: Dict[str, Any], tool_context: ToolContext
    ) -> Optional[dict]:
        """Count tool calls."""
        self.tool_count += 1
        print(f"[Plugin] Tool '{tool.name}' is about to be called.")
        # print(f"tool_context: {tool_context}")
        print(f"[Plugin] Tool call count: {self.tool_count}")

        # print(f"[Plugin] Preventing tool '{tool.name}' from being called.")
        # tool_context._invocation_context.end_invocation = True
        return

    async def after_tool_callback(
            self, *, tool: BaseTool, tool_args: Dict[str, Any], tool_context: ToolContext, result: dict
    ) -> Optional[dict]:
        print(f"[Plugin] Tool '{tool.name}' has been called.")
        # print(f"tool_context: {tool_context}")
        # print(f"result: {result}")
