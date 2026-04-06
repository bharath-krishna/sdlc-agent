# SDLC Agent - Multi-Agent Development System

An intelligent software development lifecycle agent system built with **Google ADK** that orchestrates code planning, implementation, and validation through coordinated multi-agent workflows.

## Overview

The SDLC Agent is a sophisticated multi-agent system that automates software development tasks by breaking them down into logical stages:

1. **Planning** - Repository analysis and change planning
2. **Implementation** - Code generation and file modifications
3. **Validation** - Testing and verification

The agents communicate asynchronously through a LoopAgent orchestrator, enabling iterative refinement until the development task is complete.

## Architecture

### Core Components

```
┌─────────────────────────────────────────────────────────┐
│                    Root Agent (LoopAgent)               │
│              Orchestrates multi-agent workflow           │
└─────────────┬──────────────────────────────┬────────────┘
              │                              │
    ┌─────────▼─────────┐        ┌──────────▼──────────┐
    │  Planner Agent    │        │  Developer Agent    │
    │ (Sequential Ops)  │        │  (Code Impl)        │
    │                   │        │                      │
    │ • repo_agent      │        │ • File operations   │
    │ • change_planner  │        │ • Shell commands    │
    │ • plan_writer     │        │                      │
    │ • revisor_agent   │        │                      │
    └───────────────────┘        └──────────────────────┘
                      │                    │
                      └────────┬───────────┘
                               │
                      ┌────────▼──────────┐
                      │   Bash Agent      │
                      │ (Validation)      │
                      │                    │
                      │ • Run tests        │
                      │ • Service checks   │
                      │ • Validation       │
                      └───────────────────┘
```

### Agent Descriptions

#### Planner Agent (Sequential Orchestration)
Analyzes the repository and creates a detailed implementation plan:
- **repo_agent**: Inspects README.md, AGENTS.md, and project structure
- **change_planner_agent**: Identifies files to modify and impact analysis
- **planer_agent**: Generates detailed step-by-step implementation plan
- **revisor_agent**: Validates plan feasibility and refines recommendations

#### Developer Agent
Executes the implementation plan:
- Creates and modifies files using filesystem toolset
- Executes shell commands for code generation and setup
- Updates project structure as needed
- Supports both code creation and modification workflows

#### Bash Agent
Validates implementation quality:
- Runs test suites to verify functionality
- Checks service health and deployment readiness
- Documents errors and collects validation metrics
- Updates progress tracking and documentation

## Features

- **Multi-Agent Orchestration**: Coordinated workflow between planning, development, and validation agents
- **Iterative Refinement**: Loop-based execution with configurable iteration limits (prevents infinite loops)
- **Callback Modifiers**: `before_agent_modifier` and `before_model_modifier` for context injection
- **Model Flexibility**: Support for both LiteLLM (multi-model) and native Gemini models
- **Comprehensive Tracing**: Opik integration for monitoring and observability
- **Context Awareness**: Automatic directory listing and worktree context injection

## Tech Stack

- **Framework**: [Google ADK](https://github.com/google-cloud-python/google-cloud-python) (Agent Development Kit)
- **LLM Models**: Gemini (default) or LiteLLM for multi-model support
- **Observability**: Opik for agent execution tracing
- **Language**: Python 3.9+
- **Configuration**: Environment variables (.env)

## Setup & Installation

### Prerequisites
- Python 3.9+
- pip or uv package manager
- Google API credentials (for Gemini models)
- Environment variables configured in `.env`

### Installation

```bash
# Install dependencies
pip install -r requirements.txt
# or using uv
uv sync

# Configure environment
cp .env.example .env
# Edit .env with your API keys and model preferences
```

### Configuration

The system supports configuration via environment variables:

```env
# Model Configuration
USE_LITELLM=false              # Use LiteLLM for multi-model support
MODEL_NAME=gemini-2.5-pro      # Default model name

# Telemetry & Tracing
OPIK_PROJECT_NAME=SDLCAgentTracing
OPIK_API_KEY=your_opik_api_key
```

## Running the Agent

### Basic Usage

```python
from sdlc_agent.agent import root_agent

# Execute a development task
response = root_agent.run("Implement user authentication with JWT")
```

### Opik Monitoring

1. Start the Opik server:
```bash
cd /path/to/opik
./opik.sh
# Access dashboard at http://localhost:5173
```

2. Agent executions will be automatically traced and visible in Opik dashboard

## Project Structure

```
sdlc-agent/
├── sdlc_agent/
│   ├── agent.py              # Main agent definitions and orchestration
│   └── __init__.py
├── common/
│   ├── tools.py              # Filesystem and shell toolsets
│   └── custom_agents/
│       └── planner_agent.py   # Planner sub-agents
├── doll_shop/                # Example FastAPI application (for testing)
├── demos/                    # Example demonstrations
├── main.py                   # Doll Shop FastAPI app
├── agent_app.py              # Agent application entry point
├── .env                      # Configuration (API keys, model settings)
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Example Application: Doll Shop API

The project includes a **Doll Shop FastAPI application** used as an example for testing and validating the SDLC Agent functionality.

### Features
- **Inventory Management**: CRUD operations for doll inventory
- **Reservation System**: Book and manage playtime slots
- **Validation**: Automatic checks for availability and overlapping bookings
- **Quick Utilities**: Pricing and shipping information endpoints

### Running the Doll Shop API

```bash
# Start the FastAPI server
uvicorn main:app --reload

# Access API documentation
# Swagger UI: http://127.0.0.1:8000/docs
# ReDoc: http://127.0.0.1:8000/redoc
```

### API Endpoints

**Dolls**
- `GET /dolls` - List all dolls (with optional type filter)
- `POST /dolls` - Add a new doll
- `GET /dolls/{doll_id}` - Get doll details
- `PUT /dolls/{doll_id}` - Update doll
- `DELETE /dolls/{doll_id}` - Remove doll

**Reservations**
- `POST /reservations` - Book playtime
- `GET /reservations` - View all reservations
- `DELETE /reservations/{res_id}` - Cancel reservation

**Utilities**
- `GET /dolls/{doll_id}/price-check` - Quick pricing lookup

## Callback Modifiers

The agent system includes two callback modifiers for context enhancement:

### before_agent_modifier
- Executes before tool calls
- Captures filesystem context (directory listings)
- Stores timing metrics
- Injects worktree context into callback state

### before_model_modifier
- Executes before LLM requests
- Adds filesystem context to system instructions
- Enables models to understand current environment state
- Supports both Gemini and LiteLLM model formats

## Observability & Monitoring

### Opik Tracing
The agent is instrumented with Opik for comprehensive execution monitoring:

```python
from opik.integrations.adk import OpikTracer, track_adk_agent_recursive

opik_tracer = OpikTracer(
    name="sdlc_agent_tracing",
    tags=["SDLCAgent", "agent", "google-adk"],
    project_name="SDLCAgentTracing"
)

track_adk_agent_recursive(root_agent, opik_tracer)
```

**Available but Optional:**
- Google ADK Instrumentation (commented)
- Langfuse observability integration (commented)

## Development

### Adding Custom Tools

Tools are registered in `common/tools.py` and can be:
1. Filesystem operations (file I/O, directory management)
2. Shell commands (system inspection, testing)
3. Custom integrations (APIs, external services)

### Adding Sub-Agents

Create new agents by extending `LlmAgent` or `BaseAgent` and register with the appropriate orchestrator.

## Error Handling

The bash agent collects and documents errors:
- Validation failures are logged
- Error summaries updated in `progress.md`
- Documentation updated in `README.md` and `claude.md`
- Errors do not halt execution (agent continues to next iteration)

## Limitations & Future Work

- **Max Iterations**: Configurable loop limit (default: 5) prevents infinite loops
- **Context Window**: Large codebases may require context management strategies
- **Model Switching**: Requires configuration change (doesn't switch mid-execution)
- **Tool Access**: Sub-agents limited to specified toolsets

## Contributing

This is an experimental SDLC Agent implementation. Contributions welcome for:
- Additional validation strategies
- New agent types
- Tool integrations
- Observability improvements

## References

- [Google ADK Documentation](https://github.com/google-cloud-python/google-cloud-python)
- [Opik Tracing Guide](https://www.opik.ai/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

**Last Updated**: April 2026
**Status**: Active Development
