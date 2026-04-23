# AGENTS.md — SDLC Agent System

This file documents the agent architecture, roles, tools, plugins, and conventions for the `sdlc-agent` project. It is injected into every agent's system instruction at runtime by `ContextBuildePlugin`.

---

## System Overview

This is a **Google ADK**-based multi-agent system that automates software development lifecycle tasks. Agents collaborate to plan, implement, and validate code changes in a target project directory (default: `/home/bharath/workspace/agent-playground/doll_shop`).

The entry point is `agent_app.py`, which creates an `InMemoryRunner` around the `App` object defined in `sdlc_agent/agent.py`. The same app is also exposed as an **A2A** endpoint via `to_a2a(root_agent)`.

---

## Project Structure

```
sdlc-agent/
├── agent_app.py                        # Entry point: InMemoryRunner + async main()
├── sdlc_agent/
│   ├── agent.py                        # App, root_agent, developer/test agents, plugins, compaction
│   └── sub_agents/
│       └── code_executor/
│           └── agent.py               # Sandboxed Python code executor (BuiltInCodeExecutor)
├── common/
│   ├── tools.py                        # Legacy tools file (same content as common/tools/__init__.py)
│   ├── tools/
│   │   ├── __init__.py                 # MCP toolsets + todo tools
│   │   └── todo_tools.py
│   ├── plugins/
│   │   ├── context_builder.py          # ContextBuildePlugin — injects README/AGENTS/MEMORY context
│   │   ├── debugging_plugin.py         # DebuggingPlugin — lifecycle logging + runtime env injection
│   │   └── token_tracker.py            # TokenTracker — token counting + threshold warnings
│   └── custom_agents/
│       ├── custom_agent.py             # CustomAgent — thin Agent wrapper with model injection
│       └── planner_agent.py            # PlannerAgent + repo/planer/revisor sub-agents
├── demos/                              # Demo markdown files
├── main.py                             # Doll Shop FastAPI app
└── MEMORY.md                           # Agent-writable session memory (loaded by ContextBuildePlugin)
```

---

## Agent Hierarchy

```
App (sdlc_agent)
└── root_agent = developer_agent          ← currently active
    (LoopAgent with planner+dev+test      ← commented out, kept for reference)

PlannerAgent (custom BaseAgent)
└── SequentialAgent
    ├── repo_agent        (LlmAgent, read-only fs)
    ├── planer_agent      (LlmAgent, read-only fs)
    └── revisor_agent     (LlmAgent, read-only fs)

developer_agent           (LlmAgent, full fs + shell + tavily + todos)
test_agent                (LlmAgent, full fs + shell + todos)
code_executor_agent       (LlmAgent, BuiltInCodeExecutor — sandboxed Python)
```

---

## Agents

### `developer_agent`
**File**: [sdlc_agent/agent.py:242](sdlc_agent/agent.py#L242)
**Role**: Current `root_agent`. Implements code based on the planner's output. Creates/modifies files, runs shell commands, manages todos.
**Tools**: `filesystem_toolset`, `run_shell_command`, `tavily_toolset`, todo tools
**Output key**: `developer_output`
**Constraints**: max_output_tokens=2500, timeout=10min

### `test_agent`
**File**: [sdlc_agent/agent.py:274](sdlc_agent/agent.py#L274)
**Role**: Validates developer output by running pytest and checking service health. Reads `{{developer_output}}` from session state.
**Tools**: `filesystem_toolset`, `run_shell_command`, todo tools
**Output key**: `final_results`

### `PlannerAgent`
**File**: [common/custom_agents/planner_agent.py:136](common/custom_agents/planner_agent.py#L136)
**Role**: Custom `BaseAgent` that orchestrates three read-only sub-agents sequentially via `SequentialAgent`. Currently only `repo_agent` executes (`_run_async_impl` yields only from `repo_agent`).

#### `repo_agent`
**File**: [common/custom_agents/planner_agent.py:45](common/custom_agents/planner_agent.py#L45)
**Role**: Reads `README.md` and `AGENTS.md`, inspects repo structure, produces insights.
**Tools**: read-only filesystem (`read_text_file`, `list_directory`, `directory_tree`)
**Output key**: `repo_insights`

#### `planer_agent`
**File**: [common/custom_agents/planner_agent.py:73](common/custom_agents/planner_agent.py#L73)
**Role**: Consumes `{{repo_insights}}` and writes a detailed implementation plan.
**Tools**: read-only filesystem
**Output key**: `implementation_plan`

#### `revisor_agent`
**File**: [common/custom_agents/planner_agent.py:98](common/custom_agents/planner_agent.py#L98)
**Role**: Reviews `{{implementation_plan}}` against original user intent, returns revised final plan.
**Tools**: read-only filesystem
**Output key**: `revised_plan`

### `code_executor_agent`
**File**: [sdlc_agent/sub_agents/code_executor/agent.py:13](sdlc_agent/sub_agents/code_executor/agent.py#L13)
**Role**: Safely runs Python code snippets in a sandboxed environment using `BuiltInCodeExecutor`. Validates, executes, and debugs code.
**Model**: `gemini-2.5-flash` (hardcoded)

### `CustomAgent`
**File**: [common/custom_agents/custom_agent.py:29](common/custom_agents/custom_agent.py#L29)
**Role**: Thin subclass of `Agent` that injects the configured model from env at instantiation. Inherit from this instead of `Agent` to pick up `USE_LITELLM`/`MODEL_NAME` automatically.

---

## Tools

### MCP Toolsets (via `common/tools/__init__.py`)

| Toolset | Write? | Scope |
|---|---|---|
| `filesystem_toolset` | Yes | Full read+write on `$PROJECT_DIR` |
| `readonly_filesystem_toolset` | No | Read-only subset on `$PROJECT_DIR` |
| `get_filesystem_toolset(tool_filter)` | Configurable | Factory; pass list of allowed tool names |
| `memory_toolset` | Yes | Knowledge graph via `@modelcontextprotocol/server-memory` |
| `tavily_toolset` | N/A | Web search via Tavily MCP (StreamableHTTP) |

`$PROJECT_DIR` = `/home/bharath/workspace/agent-playground/$PROJECT_NAME` (env default: `doll_shop`)

### Native Python Tools

| Function | Description |
|---|---|
| `run_shell_command(command)` | Runs bash in `PROJECT_DIR`. Returns `{output}` or `{error, output}`. |
| `exit_loop(tool_context)` | Sets `actions.escalate=True` to terminate a `LoopAgent` iteration. |
| `get_documentation_files()` | Reads `README.md`, `AGENTS.md`, `progress.md`, `CLAUDE.md` from `$PROJECT_DIR`. |

### Todo Tools (session state, key: `sdlc_todos`)

| Function | Description |
|---|---|
| `get_todos(tool_context)` | Returns all todos from session state. |
| `add_todo(title, description, priority)` | Creates a todo with status `pending`. |
| `update_todo(todo_id, ...)` | Updates title/description/status/priority. Status: `pending`/`in_progress`/`done`. |
| `remove_todo(todo_id)` | Deletes a todo by id. |
| `clear_todos()` | Clears all todos. Returns count cleared. |

Todos are persisted in `ToolContext.state["sdlc_todos"]` and visible to all agents within the same session. The `before_model_modifier` callback also injects the current todo list into every agent's system instruction.

---

## Plugins

All plugins are registered in the `App` in [sdlc_agent/agent.py:510](sdlc_agent/agent.py#L510).

### `GlobalInstructionPlugin`
Injects a global system prompt into every agent. Current content establishes:
- English-only, markdown formatting
- No secrets/credentials/PII in output
- Stop on unrecoverable error — do not guess
- File paths are relative to project root unless absolute
- Active project path: `/home/bharath/workspace/agent-playground/doll_shop`

### `ReflectAndRetryToolPlugin`
Retries failed tool calls up to 6 times with reflection. Agents should not implement their own retry loops.

### `SaveFilesAsArtifactsPlugin`
Automatically persists file-type tool outputs as ADK artifacts.

### `LoggingPlugin`
ADK built-in structured logging for all agent/model/tool events.

### `TokenTracker`
**File**: [common/plugins/token_tracker.py](common/plugins/token_tracker.py)
Tracks cumulative token usage per session. Logs a warning when `total_token_count` exceeds `TOKEN_THRESHOLD` (30,000). Counts: agent runs, LLM requests, tool calls.

### `ContextBuildePlugin`
**File**: [common/plugins/context_builder.py](common/plugins/context_builder.py)
Before every model call, reads `README.md`, `AGENTS.md`, and `MEMORY.md` from the project root and appends them to the agent's system instruction. Also pretty-prints the full system instruction to the console via `rich`.

**This is why AGENTS.md matters** — it is automatically read and injected at each LLM call.

### `DebuggingPlugin`
**File**: [common/plugins/debugging_plugin.py](common/plugins/debugging_plugin.py)
Logs agent start/stop, LLM request/response, and tool call/result. Also injects current date and time (`## Runtime Environment`) into every agent's system instruction via `llm_request.append_instructions`.

---

## App Configuration

**File**: [sdlc_agent/agent.py:502](sdlc_agent/agent.py#L502)

```python
App(
    name="sdlc_agent",
    root_agent=root_agent,
    plugins=[...],                          # see Plugins section
    events_compaction_config=EventsCompactionConfig(
        compaction_interval=5,              # compact after 5 user invocations
        overlap_size=2,                     # keep 2 invocations for continuity
        summarizer=CustomSummarizer(...),   # 7-section structured LLM summary
        token_threshold=30000,              # primary trigger: compact at 30K tokens
        event_retention_size=15,            # keep 15 raw events post-compaction
    )
)
```

**`CustomSummarizer`** ([sdlc_agent/agent.py:387](sdlc_agent/agent.py#L387)): Extends `LlmEventSummarizer` to produce a structured 7-section summary (Overview, Participants, Issues, Goals, Plan, Next Steps, Todos). Uses `gemini-3-flash-preview` for summarization.

---

## Model Configuration

Controlled by environment variables (`.env`):

| Variable | Default | Description |
|---|---|---|
| `USE_LITELLM` | `false` | Use LiteLLM wrapper (enables multi-model; disables `google_search`) |
| `MODEL_NAME` | `gemini-2.5-pro` | Model identifier. If `USE_LITELLM=true` and model starts with `gemini`, prefix `gemini/` is added automatically. |
| `PROJECT_NAME` | `doll_shop` | Subdirectory under `/home/bharath/workspace/agent-playground/` |
| `TAVILY_API_KEY` | — | Required for `tavily_toolset` web search |
| `OPIK_API_KEY` | — | Required for Opik tracing |
| `OPIK_PROJECT_NAME` | `SDLCAgentTracing` | Opik project for traces |

---

## Observability

Opik tracing is configured in [sdlc_agent/agent.py:363](sdlc_agent/agent.py#L363) via `OpikTracer` and `track_adk_agent_recursive`. All agent executions are traced to the `SDLCAgentTracing` project.

To start Opik locally:
```bash
cd /home/bharath/workspace/opik && ./opik.sh
# Dashboard: http://localhost:5173
```

---

## Running the Agent

```bash
# Install dependencies
uv sync

# Run with InMemoryRunner
python agent_app.py

# Run with ADK web UI
adk web
```

---

## Extending the System

### Adding a new agent
1. Define an `LlmAgent` or subclass of `BaseAgent`.
2. Give it a unique `name`, `description`, `instruction`, and `output_key`.
3. Register it as a sub-agent of a `SequentialAgent`, `LoopAgent`, or directly as `root_agent`.

### Adding a new tool
1. Define a Python function with type-annotated parameters and a docstring.
2. If it needs session state, add `tool_context=None` as the last parameter — ADK injects it.
3. Add the function to the appropriate agent's `tools` list.

### Adding a new plugin
1. Subclass `BasePlugin` from `google.adk.plugins`.
2. Override the lifecycle hooks you need (`before_model_callback`, `after_tool_callback`, etc.).
3. Add an instance to the `plugins` list in `App(...)`.

### Updating agent instructions
- `GlobalInstructionPlugin` instruction: edit the string in `App(plugins=[GlobalInstructionPlugin(...)])` in [sdlc_agent/agent.py:511](sdlc_agent/agent.py#L511).
- Per-agent instruction: edit the `instruction=` field on the agent definition.
- Cross-session context: write to `MEMORY.md` — `ContextBuildePlugin` injects it automatically.
