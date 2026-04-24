import os
import time
import subprocess
import litellm

from google.adk.agents.llm_agent import Agent, LlmAgent
from google.adk.agents.loop_agent import LoopAgent
from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.agents.parallel_agent import ParallelAgent
from google.adk.models.lite_llm import LiteLlm

from google.adk.tools import ToolContext
from google.genai import types
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from typing import Optional
from common.custom_agents.planner_agent import planner_agent
from common.tools import memory_toolset, tavily_toolset, list_skills, get_skill
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams, StreamableHTTPConnectionParams
from google.adk.agents.context_cache_config import ContextCacheConfig
from pydantic import BaseModel
# from langfuse import get_client
from openinference.instrumentation.google_adk import GoogleADKInstrumentor
from google.adk.plugins.save_files_as_artifacts_plugin import SaveFilesAsArtifactsPlugin
from google.adk.plugins.context_filter_plugin import ContextFilterPlugin
from google.adk.plugins.logging_plugin import LoggingPlugin
from google.adk.plugins.global_instruction_plugin import GlobalInstructionPlugin
from google.adk.plugins.reflect_retry_tool_plugin import ReflectAndRetryToolPlugin

from google.adk.agents.llm_agent import Agent
from google.adk.apps import App
from google.adk.apps.app import EventsCompactionConfig
from google.adk.apps.llm_event_summarizer import LlmEventSummarizer
from google.adk.models import Gemini
from common.plugins.token_tracker import TokenTracker
from common.plugins.debugging_plugin import DebuggingPlugin
from common.plugins.context_builder import ContextBuildePlugin
from google.genai.types import Content
from google.genai.types import Part
from google.adk.events.event import Event
from google.adk.events.event_actions import EventActions, EventCompaction
from google.adk.environment import LocalEnvironment
from google.adk.tools.environment import EnvironmentToolset




from common.custom_agents.custom_agent import CustomAgent

from dotenv import load_dotenv

load_dotenv() # load API keys and settings

# Configure model based on USE_LITELLM setting
use_litellm = os.getenv("USE_LITELLM", "false").lower() == "true"
model_name = os.getenv("MODEL_NAME", "gemini-2.5-pro")
# litellm._turn_on_debug()

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

# --- Tool Definition ---
def exit_loop(tool_context: ToolContext):
    """Call this function when there is no more work to be done and the task is complete. This signals the iterative process should end."""
    print(f"  [Tool Call] exit_loop triggered by {tool_context.agent_name}")
    tool_context.actions.escalate = True
    tool_context.actions.skip_summarization = True
    # Return empty dict as tools should typically return JSON-serializable output
    return {}



# def before_agent_modifier(
#     callback_context: CallbackContext
# ) -> Optional[ToolContext]:
#     """Inspects/modifies the tool context or skips the tool call."""
#     agent_name = callback_context.agent_name
#     print(f"  [Before Agent Call] Agent: {agent_name}")
#     # Example: You can modify the tool context here based on the agent or other factors
#     worktree_context = ""
#     try:
#         worktree_context = subprocess.check_output(['ls', '-lha', 'doll_shop'], text=True)
#     except Exception as e:
#         worktree_context = f"Error getting directory listing: {e}"
#     callback_context.state["worktree_context"] = worktree_context

#     # Store start time for metrics
#     callback_context.state["_last_tool_start"] = time.time()
    
#     return None

def before_model_modifier(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """Inspects/modifies the LLM request or skips the call."""
    agent_name = callback_context.agent_name
    print(f"  [Before Model Call] Agent: {agent_name}, Model: {llm_request.model}")
    # Example: You can modify the model or the input here based on the agent or other
    # get the filesystem worktree of the current dir

    try:
        worktree_context = subprocess.check_output(['ls', '-lha'], text=True)
    except Exception as e:
        worktree_context = f"Error getting directory listing: {e}"

    # Add profile context to system instruction
    original_instruction = llm_request.config.system_instruction or types.Content(
        role="system", parts=[]
    )

    # Ensure system_instruction is Content and parts list exists
    if not isinstance(original_instruction, types.Content):
        original_instruction = types.Content(
            role="system", parts=[types.Part(text=str(original_instruction))]
        )
    if not original_instruction.parts:
        original_instruction.parts = [types.Part(text="")]

    # Modify the text of the first part with worktree context and todos
    if original_instruction.parts and len(original_instruction.parts) > 0:
        modified_text = worktree_context + "\n\n" + (original_instruction.parts[0].text or "")
        original_instruction.parts[0].text = modified_text

    # TODO: Check model type to set system_instruction appropriately

    # For litellm models, we need to set it as string
    llm_request.config.system_instruction = original_instruction.parts[0].text
    # for Gemini models, we need to set it as Content
    # llm_request.config.system_instruction = original_instruction

    # Store start time for metrics
    callback_context.state["_last_request_start"] = time.time()

    return None

class PlannerAgentOutput(BaseModel):
    name: str
    revised_plan: str
    next_steps: str
    todos: list[str]
    finished_planing: bool

# planner_agent = LlmAgent(
#     model=model,
#     name='planner_agent',
#     description="""
#     An agent that creates a plan to answer user questions.
#     """,
#     instruction="""
# You are a file search specialist for SDLC Agent. You excel at thoroughly navigating and exploring codebases.

# === CRITICAL: READ-ONLY MODE - NO FILE MODIFICATIONS ===
# This is a READ-ONLY exploration task. You are STRICTLY PROHIBITED from:
# - Creating new files (no Write, touch, or file creation of any kind)
# - Modifying existing files (no Edit operations)
# - Deleting files (no rm or deletion)
# - Moving or copying files (no mv or cp)
# - Creating temporary files anywhere, including /tmp
# - Using redirect operators (>, >>, |) or heredocs to write to files
# - Running ANY commands that change system state

# Your role is EXCLUSIVELY to search and analyze existing code. You do NOT have access to file editing tools - attempting to edit files will fail.

# Your strengths:
# - Rapidly finding files using glob patterns
# - Searching code and text with powerful regex patterns
# - Reading and analyzing file contents

# Guidelines:
# - Use Bash tools when you know the specific file path you need to read
# - Use Bash ONLY for read-only operations (ls, git status, git log, git diff, find, grep, cat, head, tail)
# - NEVER use Bash for: mkdir, touch, rm, cp, mv, git add, git commit, npm install, pip install, or any file creation/modification
# - Adapt your search approach based on the thoroughness level specified by the caller
# - Communicate your final report directly as a regular message - do NOT attempt to create files

# NOTE: You are meant to be a fast agent that returns output as quickly as possible. In order to achieve this you must:
# - Make efficient use of the tools that you have at your disposal: be smart about how you search for files and implementations
# - Wherever possible you should try to spawn multiple parallel tool calls for grepping and reading files

# Complete the user's search request efficiently and report your findings clearly.

# Previous status result (if present):
# {{final_results || "No previous results, this is the first step."}}
# """,
#     tools=[
#         # get_filesystem_toolset(tool_filter=["read_text_file", "list_directory", "directory_tree", "read_multiple_files", "search_files"]),
#         filesystem_toolset,
#         run_shell_command,
#         # memory_toolset,
#         # exit_loop
#     ],
#     output_key='revised_plan',
#     # output_schema=PlannerAgentOutput
# )

class DeveloperAgentOutput(BaseModel):
    status: str
    num_files_changed: int
    list_of_files_changed: list[str]
    any_errors: Optional[str]
    notes_for_test_agent: Optional[str]

developer_agent = Agent(
    model=model,
    name='developer_agent',
    description="""
    An agent that implements code based on the plan provided by the planner_agent.
    """,
    instruction="""
    You are a developer agent responsible for implementing code based on the plan provided by the planner_agent. You will receive a plan that outlines the specific tasks you need to accomplish. Your primary responsibility is to write code, create files, and organize folders as needed to execute the plan effectively
    """,
    tools=[
        tavily_toolset,
        list_skills,
        get_skill,
        EnvironmentToolset(
            environment=LocalEnvironment(
                working_dir=os.environ.get("PROJECT_ROOT", "/home/bharath/workspace/agent-playground/doll_shop")
            ),
        ),
    ],
    output_key="developer_output",
    # generate_content_config=types.GenerateContentConfig(
    #     # temperature=0.2, # More deterministic output
    #     max_output_tokens=2500,
    #     http_options=types.HttpOptions(
    #         timeout=600000  # 10 minutes
    #     )
    # ),
    # input_schema=PlannerAgentOutput,
    # output_schema=DeveloperAgentOutput
)

test_agent = Agent(
    model=model,
    name='test_agent',
    description="An agent that runs pytest cases and checks if the service can be run smoothly, noting any errors in the output.",
    instruction="""
    You are a test agent responsible for running pytest cases to validate the code and checking if the service can be run smoothly. Execute pytest commands to run tests, and attempt to start or run the service to verify it operates without errors. If any tests fail or the service encounters issues, collect and document the errors in a string format under the output key "test_results". Provide a summary of the test results and any errors encountered.
    Developer Output:
    {{developer_output || "No developer output available."}}
    """,
    output_key="final_results",
    # generate_content_config=types.GenerateContentConfig(
    #     # temperature=0.2, # More deterministic output
    #     max_output_tokens=2500,
    #     http_options=types.HttpOptions(
    #         timeout=600000  # 10 minutes
    #     )
    # ),
    # input_schema=DeveloperAgentOutput
)

# root_agent = CustomAgent(
#     name='sdlc_agent',
#     description='An intelligent SDLC orchestrator that coordinates planning, development, and testing agents to deliver complete software solutions.',
#     # instruction="""
#     # You are an SDLC (Software Development Life Cycle) agent that orchestrates a complete software development workflow. You coordinate three specialized agents:
    
#     # 1. Planner Agent: Analyzes user requirements and creates detailed development plans
#     # 2. Developer Agent: Implements code changes and develops features based on the plan
#     # 3. Test Agent: Runs tests and validates that the code works correctly
    
#     # Your responsibility is to:
#     # - Receive user requests or requirements
#     # - Delegate planning tasks to the planner agent
#     # - Coordinate development work through the developer agent
#     # - Ensure quality through the test agent
#     # - Synthesize results and provide comprehensive feedback to the user
    
#     # Always ensure proper sequencing: first plan, then develop, then test. Handle any errors gracefully and report them to the user.
#     # """,
#     # tools=[
#     #     memory_toolset,
#     # ],
#     sub_agents=[
#         planner_agent,
#         developer_agent,
#         test_agent,
#     ],
#     # before_model_callback=before_model_modifier,
#     # max_iterations=2,  # Set a reasonable limit to prevent infinite loops
# )

# from sdlc_agent.sub_agents.code_executor.agent import code_executor_agent
root_agent = developer_agent  # For now, we will just run the developer agent directly to test it out. We will integrate the full loop with the planner and test agents later.

from google.adk.a2a.utils.agent_to_a2a import to_a2a

# Load A2A agent card from a file
a2a_app = to_a2a(root_agent)


# # Initialize Langfuse
# langfuse = get_client()

# # Verify connection (skip if not configured)
# try:
#     if langfuse.auth_check():
#         print("Langfuse client is authenticated and ready!")
#     else:
#         print("Langfuse client not properly configured. Skipping authentication check.")
# except Exception as e:
#     print(f"Langfuse authentication check skipped: {type(e).__name__}")


# make sure to start opik
# cd /home/bharath/workspace/opik
# ./opik.sh
# http://localhost:5173

from opik.integrations.adk import OpikTracer, track_adk_agent_recursive

# Configure Opik tracer
opik_tracer = OpikTracer(
    name="sdlc_agent_tracing",
    tags=["SDLCAgent", "agent", "google-adk"],
    metadata={
        "environment": "development",
        "model": os.environ.get("MODEL_NAME", "openai/qwen3-coder-next:q4_K_M"),
        "framework": "google-adk",
        "example": "basic"
    },
    project_name="SDLCAgentTracing"
)
# Instrument the agent with a single function call - this is the recommended approach
track_adk_agent_recursive(root_agent, opik_tracer)

# Define the AI model to be used for summarization:
summarization_llm = Gemini(model="gemini-3-flash-preview")
# summarization_llm = model  # Use the same model as the agents for summarization to reduce complexity (can be different if desired)


# Create the summarizer with the custom model:
# my_summarizer = LlmEventSummarizer(llm=summarization_llm)

class CustomSummarizer(LlmEventSummarizer):
    """A custom summarizer that extends the base LlmEventSummarizer to include additional context or formatting."""

    def _format_events_for_prompt(self, events: list[Event]) -> str:
        """Formats a list of events into a string for the LLM prompt, with custom formatting."""
        formatted_events = []
        for event in events:
            actions_str = "\n".join(str(a) for a in event.actions) if event.actions else "No actions"
            formatted_event = f"Author: {event.author}\nActions: {actions_str}\nContent: {event.content}\n---"
            formatted_events.append(formatted_event)
        return "\n".join(formatted_events)

    async def maybe_summarize_events(
        self, *, events: list[Event]
    ) -> Optional[Event]:
        """Compacts given events and returns the compacted content, with custom summarization logic."""
        if not events:
            return None

        # You can add custom logic here to determine when to summarize or how to format the prompt
        conversation_history = self._format_events_for_prompt(events)
        prompt = f"""Analyze and summarize the following conversation history in a structured format.

CONVERSATION HISTORY:
{conversation_history}

PROVIDE A DETAILED SUMMARY INCLUDING:

1. **Overview**
   - Total number of events/messages summarized
   - Time span of the conversation
   - Primary objective or context

2. **Participants & Roles**
   - List all distinct roles/participants involved
   - Brief description of each role's involvement

3. **Key Issues & Observations**
   - Technical issues identified
   - Blockers or challenges mentioned
   - Important decisions made
   - Risks or concerns raised

4. **Goals & Objectives**
   - What the team is trying to achieve
   - Success criteria if mentioned
   - Project milestones

5. **Plan & Strategy**
   - Approach or strategy discussed
   - Architecture decisions
   - Implementation plan

6. **Next Steps**
   - Immediate action items
   - Upcoming milestones
   - Dependency items

7. **Todo Items**
   - Specific tasks to be completed
   - Owner (if identified)
   - Priority or deadline (if mentioned)

Format the summary clearly with headers and bullet points. Be concise but comprehensive."""

        llm_request = LlmRequest(
            model=self._llm.model,
            contents=[Content(role='user', parts=[Part(text=prompt)])],
        )
        summary_content = None
        print((f"Compacting {len(events)} events into a summary."))
        # # content of first event
        # print(f"******************** First event content: {events[0].content} ********************")

        # # content of last event
        # print(f"******************** Last event content: {events[-1].content} ********************")
        async for llm_response in self._llm.generate_content_async(
            llm_request, stream=False
        ):
            if llm_response.content:
                summary_content = llm_response.content
                break

        if summary_content is None:
            return None

        # Ensure the compacted content has the role 'model'
        summary_content.role = 'model'

        start_timestamp = events[0].timestamp
        end_timestamp = events[-1].timestamp

        # Create a new event for the summary using EventCompaction
        # The summary must live in event.actions.compaction.compacted_content per ADK contract
        summary_event = Event(
            author="user",
            invocation_id=Event.new_id(),
            actions=EventActions(
                compaction=EventCompaction(
                    start_timestamp=start_timestamp,
                    end_timestamp=end_timestamp,
                    compacted_content=summary_content,
                )
            ),
        )

        print(f"  [Custom Summarizer] Created summary event with content: {summary_content}")

        return summary_event


my_summarizer = CustomSummarizer(llm=summarization_llm)

TOKEN_THRESHOLD = 30000  # Set token threshold for compaction (adjust based on your needs)

app = App(
    name="sdlc_agent",
    root_agent=root_agent,
    # context_cache_config=ContextCacheConfig(
    #     # min_tokens=4096,
    #     ttl_seconds=600,  # 10 mins for research sessions
    #     cache_intervals=10,
    # ),
    plugins=[
        GlobalInstructionPlugin(
            global_instruction="""
You are part of an SDLC automation system. The following rules apply to all agents in this system:

- Always respond in English using clear, concise markdown formatting.
- Never expose, log, or include secrets, credentials, API keys, or PII in any output.
- If you encounter an unrecoverable error or ambiguous input, report it clearly and stop — do not silently skip or guess.
- All file operations are relative to the project root unless an absolute path is provided.
- Be precise: only perform the task assigned to you. Do not take actions outside your defined scope.
The path of the project you are working on is:
/home/bharath/workspace/agent-playground/doll_shop
"""),
        ReflectAndRetryToolPlugin(max_retries=6),
        # SaveFilesAsArtifactsPlugin(),
        ContextFilterPlugin(
            name="context_filter",
            num_invocations_to_keep=15,
            # custom_filter=lambda context: [entry for entry in context if "test_agent" not in entry.agent_name]
        ),
        LoggingPlugin(),
        TokenTracker(summarization_llm=summarization_llm, token_threshold=TOKEN_THRESHOLD),
        ContextBuildePlugin(),
        # DebuggingPlugin(),
    ],
    events_compaction_config=EventsCompactionConfig(
        compaction_interval=5,    # Fallback: trigger compaction after 5 user invocations (very aggressive).
        overlap_size=2,           # Keep last 2 invocations from previous window for continuity.
        summarizer=my_summarizer,
        token_threshold=TOKEN_THRESHOLD,    # Primary trigger: compact when tokens reach 40% of 250K context (leaves 150K free).
        event_retention_size=15,   # Keep last 15 raw (unsummarized) events for recent context after compaction.
    ),
    # Optionally include App-level features:
    # plugins, context_cache_config, resumability_config
)

# # Instrument with Google ADK (after app is created to avoid pydantic v1 conflicts)
# try:
#     GoogleADKInstrumentor().instrument()
# except Exception as e:
#     print(f"Warning: Failed to instrument with OpenInference: {e}")
