# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
uv sync

# Run the agent (InMemoryRunner, single task)
python agent_app.py

# Run the ADK web UI (chat interface on port 8002)
adk web

# Run as A2A API server
adk api_server

# Run ADK dev UI against a specific module
adk web sdlc_agent.agent
```

Environment variables live in `sdlc_agent/.env`. Copy and configure before running:
```bash
cp sdlc_agent/.env sdlc_agent/.env.local  # edit with your keys
```

Required env vars: `GOOGLE_API_KEY` or `OPENAI_API_BASE`+`OPENAI_API_KEY`, `MODEL_NAME`, `USE_LITELLM`, `TAVILY_API_KEY`, `OPIK_URL_OVERRIDE`.

## Architecture

### Entry Points and App Wiring

`agent_app.py` is the runnable entry point — it imports `app` from `sdlc_agent/agent.py` and wraps it in an `InMemoryRunner`. The same `app` object is exposed as an **A2A** endpoint via `to_a2a(root_agent)` at the bottom of `agent_app.py`.

`sdlc_agent/agent.py` is the central file. It defines all agents, registers plugins on the `App`, and configures event compaction. The `root_agent` is currently just `developer_agent` (the full `LoopAgent` with planner+developer+test is commented out but preserved).

### Agent Execution Flow

The intended (currently commented) flow is:
```
LoopAgent (max 2 iterations)
  └─ PlannerAgent → developer_agent → test_agent
```

`PlannerAgent` (`common/custom_agents/planner_agent.py`) is a custom `BaseAgent` that internally runs `repo_agent → planer_agent → revisor_agent` via `SequentialAgent`. However, only `repo_agent` currently executes — the `_run_async_impl` method only yields from `repo_agent`.

### Plugin Pipeline (runs on every LLM call)

Plugins are applied in registration order inside `App(plugins=[...])`:

1. **`GlobalInstructionPlugin`** — prepends a cross-cutting system prompt to every agent (sets project path, rules)
2. **`ReflectAndRetryToolPlugin`** — retries failed tool calls up to 6 times with reflection
3. **`SaveFilesAsArtifactsPlugin`** — auto-saves file tool outputs as ADK artifacts
4. **`LoggingPlugin`** — structured ADK lifecycle logging
5. **`TokenTracker`** — counts tokens; warns at 30K threshold
6. **`ContextBuildePlugin`** — reads `README.md`, `AGENTS.md`, `MEMORY.md` from the repo root and appends them to every agent's system instruction before each LLM call
7. **`DebuggingPlugin`** — logs lifecycle events and appends `## Runtime Environment` (date/time) to every system instruction

This means **AGENTS.md and MEMORY.md are live context** — their content is injected into every model request. Updating them changes agent behavior immediately with no code changes.

### Tools and Their Scope

All filesystem tools connect to a **target project directory**, not this repo:
```
/home/bharath/workspace/agent-playground/$PROJECT_NAME  (default: doll_shop)
```

MCP toolsets are created via `npx @modelcontextprotocol/server-filesystem` and `@modelcontextprotocol/server-memory`. The `get_filesystem_toolset(tool_filter=[...])` factory creates a filtered read-only view; use it for planning agents that must not write files.

Todo state is stored in `session.state["sdlc_todos"]` and is visible to all agents in a session. The `before_model_modifier` callback in `agent.py` also injects the current todo list into every agent's system instruction.

### Event Compaction

Compaction triggers when either:
- Token count exceeds 30K (`token_threshold`)
- 5 user invocations pass (`compaction_interval`)

`CustomSummarizer` in `sdlc_agent/agent.py` uses `gemini-3-flash-preview` to produce a structured 7-section summary. The last 15 raw events and 2 invocations of overlap are always preserved.

### Model Switching

Set in `sdlc_agent/.env`:
- `USE_LITELLM=false` + `MODEL_NAME=gemini-2.5-pro` → native Gemini (enables `google_search` tool)
- `USE_LITELLM=true` + `MODEL_NAME=openai/...` + `OPENAI_API_BASE=...` → any OpenAI-compatible local/remote server (Gemini prefix is auto-added when needed)

`code_executor_agent` hardcodes `gemini-2.5-flash` and is not affected by env vars.

### Key Patterns

- **Output keys**: agents pass data to downstream agents via `output_key` — the value is stored in session state under that key and referenced in subsequent agents' instructions as `{{key_name}}`.
- **`CustomAgent`** (`common/custom_agents/custom_agent.py`): thin `Agent` subclass that injects the env-configured model. Use it instead of `Agent` for new agents to pick up model config automatically.
- **`common/tools/`** and **`common/tools.py`** are duplicates — both contain the same toolset and todo tool definitions. The package (`common/tools/__init__.py`) is the canonical one; `common/tools.py` is the legacy file.
