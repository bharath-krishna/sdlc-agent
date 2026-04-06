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
# from common.custom_agents.planner_agent import planner_agent
from common.tools import filesystem_toolset, readonly_filesystem_toolset, get_filesystem_toolset, memory_toolset
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams, StreamableHTTPConnectionParams
from google.adk.agents.context_cache_config import ContextCacheConfig
from pydantic import BaseModel
# from langfuse import get_client
from openinference.instrumentation.google_adk import GoogleADKInstrumentor
from google.adk.plugins.save_files_as_artifacts_plugin import SaveFilesAsArtifactsPlugin
from google.adk.plugins.context_filter_plugin import ContextFilterPlugin
from google.adk.plugins.logging_plugin import LoggingPlugin
from google.adk.plugins.reflect_retry_tool_plugin import ReflectAndRetryToolPlugin


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

    import ipdb; ipdb.set_trace()

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

    # Modify the text of the first part
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

def run_shell_command(command: str, dir: str):
    """
    A simple tool to execute bash commands.
    args:
        command: The bash command to execute.
        dir: The directory to execute the command in.
    returns:
        output: The output of the command or error message if it fails.
    """
    print(f"  [Tool Call] run_shell_command executing command: {command}")
    try:
        result = subprocess.check_output(command, shell=True, text=True, cwd=dir)
        return {"output": result}
    except subprocess.CalledProcessError as e:
        return {"error": str(e), "output": e.output}

class PlannerAgentOutput(BaseModel):
    name: str
    revised_plan: str
    next_steps: str
    todos: list[str]
    finished_planing: bool

planner_agent = LlmAgent(
    model=model,
    name='planner_agent',
    description="""
    An agent that creates a plan to answer user questions.
    """,
    instruction="""
    You are a planner_agent.
1. Focus on creating a plan for the developer_agent to implement.
2. Do not write files, modify the repository, or execute code yourself.
3. You only have readonly filesystem tools, so use them only to inspect the project and gather context.
4. Analyze the user's question and the previous results.
5. Determine the next single sub-task and describe it clearly.
6. Pass the plan down to developer_agent as `revised_plan`.
7. If the overall goal is already met, summarize that and explain what the developer_agent should validate.
Previous status result (if present):
{{final_results || "No previous results, this is the first step."}}
""",
    tools=[
        get_filesystem_toolset(tool_filter=["read_text_file", "list_directory", "directory_tree", "read_multiple_files", "search_files"]),
        # filesystem_toolset,
        # memory_toolset,
        # exit_loop
    ],
    output_key='revised_plan',
    # output_schema=PlannerAgentOutput
)

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
        filesystem_toolset,
        run_shell_command,
        # exit_loop
    ],
    output_key="developer_output",
    generate_content_config=types.GenerateContentConfig(
        # temperature=0.2, # More deterministic output
        max_output_tokens=2500,
        http_options=types.HttpOptions(
            timeout=600000  # 10 minutes
        )
    ),
    # input_schema=PlannerAgentOutput,
    # output_schema=DeveloperAgentOutput
)

test_agent = Agent(
    model=model,
    name='test_agent',
    description="An agent that runs pytest cases and checks if the service can be run smoothly, noting any errors in the output.",
    instruction="""
    You are a test agent responsible for running pytest cases to validate the code and checking if the service can be run smoothly. Execute pytest commands to run tests, and attempt to start or run the service to verify it operates without errors. If any tests fail or the service encounters issues, collect and document the errors in a string format under the output key "test_results". Provide a summary of the test results and any errors encountered.
    """,
    tools=[
        run_shell_command,
        # exit_loop
    ],
    output_key="final_results",
    generate_content_config=types.GenerateContentConfig(
        # temperature=0.2, # More deterministic output
        max_output_tokens=2500,
        http_options=types.HttpOptions(
            timeout=600000  # 10 minutes
        )
    ),
    # input_schema=DeveloperAgentOutput
)

root_agent = CustomAgent(
    name='sdlc_agent',
    description='An intelligent SDLC orchestrator that coordinates planning, development, and testing agents to deliver complete software solutions.',
    instruction="""
    You are an SDLC (Software Development Life Cycle) agent that orchestrates a complete software development workflow. You coordinate three specialized agents:
    
    1. Planner Agent: Analyzes user requirements and creates detailed development plans
    2. Developer Agent: Implements code changes and develops features based on the plan
    3. Test Agent: Runs tests and validates that the code works correctly
    
    Your responsibility is to:
    - Receive user requests or requirements
    - Delegate planning tasks to the planner agent
    - Coordinate development work through the developer agent
    - Ensure quality through the test agent
    - Synthesize results and provide comprehensive feedback to the user
    
    Always ensure proper sequencing: first plan, then develop, then test. Handle any errors gracefully and report them to the user.
    """,
    # tools=[
    #     memory_toolset,
    # ],
    sub_agents=[
        planner_agent,
        developer_agent,
        test_agent,
    ],
    # before_model_callback=before_model_modifier,
    # max_iterations=2,  # Set a reasonable limit to prevent infinite loops
)

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



from google.adk.agents.llm_agent import Agent
from google.adk.apps import App
from google.adk.apps.compaction import EventsCompactionConfig
from google.adk.apps.llm_event_summarizer import LlmEventSummarizer
from google.adk.models import Gemini
from common.plugins.token_tracker import TokenTracker
from common.plugins.debugging_plugin import DebuggingPlugin

# Define the AI model to be used for summarization:
summarization_llm = Gemini(model="gemini-2.5-flash")

# Create the summarizer with the custom model:
my_summarizer = LlmEventSummarizer(llm=summarization_llm)


app = App(
    name="sdlc_agent",
    root_agent=root_agent,
    context_cache_config=ContextCacheConfig(
        # min_tokens=4096,
        ttl_seconds=600,  # 10 mins for research sessions
        cache_intervals=10,
    ),
    plugins=[
        ReflectAndRetryToolPlugin(max_retries=3),
        SaveFilesAsArtifactsPlugin(),
        ContextFilterPlugin(
            name="context_filter",
            num_invocations_to_keep=10,
            # custom_filter=lambda context: [entry for entry in context if "test_agent" not in entry.agent_name]
        ),
        LoggingPlugin(),
        TokenTracker(),
        DebuggingPlugin(),
    ],
    events_compaction_config=EventsCompactionConfig(
        compaction_interval=10,  # Trigger compaction every 3 new invocations.
        overlap_size=1,          # Include last invocation from the previous window.
        # summarizer=my_summarizer,
    ),
    # Optionally include App-level features:
    # plugins, context_cache_config, resumability_config
)

# # Instrument with Google ADK (after app is created to avoid pydantic v1 conflicts)
# try:
#     GoogleADKInstrumentor().instrument()
# except Exception as e:
#     print(f"Warning: Failed to instrument with OpenInference: {e}")
