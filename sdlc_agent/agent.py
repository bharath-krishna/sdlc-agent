import os
import time
import subprocess
import litellm

from google.adk.agents.llm_agent import Agent
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
from common.tools import filesystem_toolset, readonly_filesystem_toolset
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams, StreamableHTTPConnectionParams
from google.adk.agents.context_cache_config import ContextCacheConfig
from pydantic import BaseModel
# from langfuse import get_client
from openinference.instrumentation.google_adk import GoogleADKInstrumentor

from dotenv import load_dotenv

load_dotenv() # load API keys and settings

# Configure model based on USE_LITELLM setting
use_litellm = os.getenv("USE_LITELLM", "false").lower() == "true"
model_name = os.getenv("MODEL_NAME", "gemini-2.5-pro")

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



def before_agent_modifier(
    callback_context: CallbackContext
) -> Optional[ToolContext]:
    """Inspects/modifies the tool context or skips the tool call."""
    agent_name = callback_context.agent_name
    print(f"  [Before Agent Call] Agent: {agent_name}")
    # Example: You can modify the tool context here based on the agent or other factors
    worktree_context = ""
    try:
        worktree_context = subprocess.check_output(['ls', '-lha', 'doll_shop'], text=True)
    except Exception as e:
        worktree_context = f"Error getting directory listing: {e}"
    callback_context.state["worktree_context"] = worktree_context

    # Store start time for metrics
    callback_context.state["_last_tool_start"] = time.time()
    
    return None

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


# planner_agent = Agent(
#     model=model,
#     name='planner_agent',
#     description="""
#     An agent that creates a plan to answer user questions.
#     """,
#     instruction="""
# 1. **Analyze Goal**: Read the user's question and detect the overall goal.
# 2. **Review History & Validate**: Examine the previous interaction history. 
#    - If a sub-task was just performed by the executor, validate the result. Does it indicate success? Does it provide the data needed for the next step?
#    - If a result is an error or unexpected, plan a corrective sub-task or explain the issue.
# 3. **Determine Next Step**: Based on the validation, determine the NEXT single sub-task. If the overall goal is met and validated, provide a final response to the user.
# 4. **Retrieve Documentation**: Use the `retrieve_service_documentation` tool to fetch the API specs. This is your ONLY tool.
# 5. **DO NOT** attempt to call any other functions or API endpoints directly. 
# 6. **Progressive Disclosure**: Identify ONLY the relevant API endpoint and its parameters for the CURRENT sub-task.
# 7. **Execution Context**: Output ONLY the current sub-task description and that specific API specification in the `execution_context`.
# 8. **Final Validation**: Before finishing the entire task, ensure the final state has been verified (e.g., if a user was added, the response confirms they are now in the group).

# Current state of the project (Showing files in the project directory):
# {{worktree_context}}

# """,
#     tools=[readonly_filesystem_toolset],
#     output_key='plan',
#     before_agent_callback=before_agent_modifier,
#     # generate_content_config=types.GenerateContentConfig(
#     #     max_output_tokens=2000,
#     # )
# )

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
        run_shell_command
    ],
    # generate_content_config=types.GenerateContentConfig(
    #     max_output_tokens=2000,
    # ),
)

# root_agent = SequentialAgent(
#     name='root_agent',
#     description='A helpful assistant for user questions.',
#     sub_agents=[
#         planner_agent,
#         developer_agent,
#     ],
# )

bash_agent = Agent(
    model=model,
    name='bash_agent',
    description="An agent that executes bash commands to inspect the environment and assist with development tasks.",
    instruction="""
    You are a bash agent that can execute bash commands to inspect the environment and assist with development tasks. You have access to a tool called `run_shell_command` that allows you to run bash commands in a specified directory. Use this tool to gather information about the file system, check the status of services, or perform any other tasks that can help you accomplish your goals.  
    You only use bash commands to try and validate the developer agent's work, like running tests, running service to see if it runs properly or not.
    In case of any error you collect them and document it in the progress.md file and update readme.md and claude.md.
    """,
    tools=[
        run_shell_command,
    ],
)

root_agent = LoopAgent(
    name='root_agent',
    description='A helpful assistant for user questions.',
    sub_agents=[
        planner_agent,
        developer_agent,
        bash_agent,
    ],
    max_iterations=5,  # Set a reasonable limit to prevent infinite loops
)


# # Initialize Langfuse
# langfuse = get_client()

# # Verify connection
# if langfuse.auth_check():
#     print("Langfuse client is authenticated and ready!")
# else:
#     print("Authentication failed. Please check your credentials and host.")

# # Instrument with Google ADK
# GoogleADKInstrumentor().instrument()


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
        "model": os.environ.get("MODEL_NAME", "gemini-3-flash-preview"),
        "framework": "google-adk",
        "example": "basic"
    },
    project_name="SDLCAgentTracing"
)
# Instrument the agent with a single function call - this is the recommended approach
track_adk_agent_recursive(root_agent, opik_tracer)



# from google.adk.agents.llm_agent import Agent
# from google.adk.apps import App

# app = App(
#     name="agents",
#     root_agent=root_agent,
#     context_cache_config=ContextCacheConfig(
#         min_tokens=4096,
#         ttl_seconds=600,  # 10 mins for research sessions
#         cache_intervals=3, 
#     )
#     # Optionally include App-level features:
#     # plugins, context_cache_config, resumability_config
# )