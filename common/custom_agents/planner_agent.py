import os
import subprocess
import litellm

from google.adk.agents import Agent, LlmAgent, BaseAgent, InvocationContext, LoopAgent, SequentialAgent
from google.adk.events import Event
from google.adk.tools import ToolContext
from google.genai import types
from google.adk.models.lite_llm import LiteLlm

from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from typing import AsyncGenerator, Optional
from common.tools import filesystem_toolset, get_documentation_files, readonly_filesystem_toolset, get_filesystem_toolset
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams, StreamableHTTPConnectionParams
from google.adk.agents.context_cache_config import ContextCacheConfig
from pydantic import BaseModel


import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

import os

# Configure model based on USE_LITELLM setting
use_litellm = os.getenv("USE_LITELLM", "false").lower() == "true"
model_name = os.getenv("MODEL_NAME", "gemini-3-flash-preview")

if use_litellm:
    # Use LiteLLM for multi-model support (google_search won't work)
    if model_name.startswith("gemini") and not model_name.startswith("gemini/"):
        litellm_model = f"gemini/{model_name}"
    else:
        litellm_model = model_name
    model = LiteLlm(model=litellm_model)
    print(f"Using LiteLLM with model: {litellm_model}")
else:
    # Use native Gemini model (required for google_search tool)
    model = model_name
    print(f"Using native Gemini model: {model_name}")

repo_agent = LlmAgent(
    model=os.environ.get("MODEL_NAME", "gemini-3-flash-preview"),
    name='repo_agent',
    description="""
    An agent that inspects the code repository to provide insights about
    the project structure, architecture, and codebase organization.
    """,
    instruction="""
    You are a repository analyzer. Your task is to:
    1. Call the tools to retrieve the contents of README.md and AGENTS.md files from the repository.
    
    Use the information gathered to provide actionable insights about the codebase.
    """,
    tools=[
        get_filesystem_toolset(tool_filter=["read_text_file", "list_directory", "directory_tree"])
    ],
    output_key='repo_insights',
)


change_planner_agent = LlmAgent(
    model=os.environ.get("MODEL_NAME", "gemini-3-flash-preview"),
    name='change_planner_agent',
    description="This agent analyzes the repository structure and identifies the exact files, modules, and codebase areas that need to be modified. It provides a high-level overview and precursor plan for the plan_writer_agent to expand upon.",
    instruction="""
    You are a change planning analyst. Based on the repo insights provided, your task is to:
    1. Identify the exact files and modules that need to be modified
    2. Map out the codebase areas that will be affected by the changes
    3. Analyze dependencies and relationships between components
    4. Create a high-level precursor plan with:
       - List of files/modules to modify (with file paths)
       - Component relationships and dependencies
       - Impact analysis of proposed changes
       - Priority order for modifications
       - Key considerations and constraints
    
    This precursor plan will be used by the plan_writer_agent to create detailed implementation steps.
    
    repo_insights:
    {{repo_insights}}
    """,
    tools=[],
    output_key='files_to_modify',
)


plan_writer_agent = LlmAgent(
    model=os.environ.get("MODEL_NAME", "gemini-3-flash-preview"),
    name='plan_writer_agent',
    description="""
    An agent that takes the change plan created by the change_planner_agent and writes a detailed
    implementation plan.
    """,
    instruction="""
    The implementation plan should include specific instructions for each task in the change plan, as well as any relevant code snippets or examples.
    Files to modify:
    {{files_to_modify}}
    """,
    output_key='implementation_plan',
)

revisor_agent = LlmAgent(
    model=os.environ.get("MODEL_NAME", "gemini-3-flash-preview"),
    name='revisor_agent',
    description="""
    An agent that reviews the implementation plan created by the plan_writer_agent and evaluates it against the original user intent. It provides constructive critique and actionable feedback to ensure the plan effectively addresses the user's requirements.
    """,
    instruction="""
    You are an implementation plan reviewer. Your task is to:
    1. Review the implementation plan against the original user intent and requirements
    2. Verify that the plan adequately addresses all requested changes
    3. Check for completeness, feasibility, and alignment with the repository structure
    4. Use filesystem tools to validate file paths and module references if needed
    5. Provide specific, actionable feedback including:
       - Whether the plan fully addresses user requirements
       - Any gaps or missing components
       - Suggestions for improvement or optimization
       - Feasibility concerns or potential issues
       - Overall assessment and recommendations
    6. Return the revised and finalized implementation plan incorporating your feedback
    
    implementation_plan:
    {{implementation_plan}}
    """,
    tools=[
        get_filesystem_toolset(tool_filter=["read_text_file", "list_directory", "directory_tree"])
    ],
    output_key='revised_plan',
)


class PlannerAgent(BaseAgent):
    name: str = "planner_agent"
    description: str = "An agent that orchestrates the planning process for project repository modifications."
    repo_agent: LlmAgent
    change_planner_agent: LlmAgent
    plan_writer_agent: LlmAgent
    revisor_agent: LlmAgent
    sequential_agent: SequentialAgent

    def __init__(
            self,
            repo_agent: LlmAgent,
            change_planner_agent: LlmAgent,
            plan_writer_agent: LlmAgent,
            revisor_agent: LlmAgent,
            sequential_agent: Optional[SequentialAgent] = None
        ):

        sequential_agent = SequentialAgent(
            name=f"sequential_planner_agent",
            description="A sequential agent that orchestrates the repo analysis, change planning, plan writing, and revision process.",
            sub_agents=[
                repo_agent,
                change_planner_agent,
                plan_writer_agent,
                revisor_agent,
            ],
        )

        super().__init__(
            name="planner_agent",
            repo_agent=repo_agent,
            change_planner_agent=change_planner_agent,
            plan_writer_agent=plan_writer_agent,
            revisor_agent=revisor_agent,
            sequential_agent=sequential_agent
        )

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        # return super()._run_async_impl(ctx)
        async for event in self.sequential_agent.run_async(ctx):
            yield event


planner_agent = PlannerAgent(
    repo_agent=repo_agent,
    change_planner_agent=change_planner_agent,
    plan_writer_agent=plan_writer_agent,
    revisor_agent=revisor_agent,
)