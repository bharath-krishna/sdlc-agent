# The Enchanted Doll Shop - Backend API

This is a FastAPI-based backend for a doll shop. It provides features for managing doll inventory and scheduling playtime reservations.

## Features

- **Doll Inventory Management (CRUD)**:
    - List all dolls (with type filtering).
    - Add new dolls.
    - Retrieve detailed doll information.
    - Update doll attributes.
    - Remove dolls from inventory.
- **Playtime Reservations**:
    - Book playtime slots for dolls.
    - Automatic validation for:
        - Doll existence and availability.
        - Future reservation times.
        - Overlapping reservations (assuming 1-hour slots).
    - View all scheduled reservations.
    - Cancel reservations.
- **Quick Utility**:
    - Specialized endpoint for quick price, weight, and shipping category checks.

## Tech Stack

- **Framework**: FastAPI
- **Data Validation**: Pydantic
- **Language**: Python 3.9+
- **Database**: In-memory (for demonstration)

## Agent Architecture

```mermaid
graph TB
    subgraph Config["Configuration Layer"]
        ENV["Environment Config"]
        LITELLM["LiteLLM Setup"]
        GEMINI["Native Gemini Setup"]
        MODEL["Model Selection"]
    end

    subgraph RootAgents["Root Agent Layer"]
        ROOT["🔴 Root Agent<br/>developer_agent"]
        PLANNER_ROOT["📋 Planner Agent<br/>Orchestrator"]
    end

    subgraph DeveloperAgents["Developer Agent"]
        DEVELOPER["👨‍💻 developer_agent<br/>Code Implementation"]
    end

    subgraph PlannerSubAgents["Planner Agent - Sub-agents<br/>(Sequential Execution)"]
        SEQ["SequentialAgent<br/>Orchestrator"]
        REPO["📁 repo_agent<br/>Repository Analyzer"]
        CHANGE_PLAN["🗂️ change_planner_agent<br/>File & Module Mapper"]
        PLAN_WRITE["✍️ plan_writer_agent<br/>Plan Generator"]
        REVISOR["👀 revisor_agent<br/>Plan Validator"]
    end

    subgraph PlannerTools["Planner Tools"]
        REPO_TOOLS["Filesystem Toolset<br/>- read_text_file<br/>- list_directory<br/>- directory_tree"]
        REVISOR_TOOLS["Filesystem Toolset<br/>- read_text_file<br/>- list_directory<br/>- directory_tree"]
    end

    subgraph DeveloperTools["Developer Tools"]
        FILESYSTEM["Filesystem Toolset<br/>- File operations<br/>- Directory handling"]
        READONLY_FS["ReadOnly Filesystem<br/>- Safe file reads<br/>- Directory inspection"]
        SHELL["run_shell_command<br/>- Execute bash commands<br/>- Environment inspection"]
    end

    subgraph Callbacks["Callback Modifiers"]
        BEFORE_AGENT["before_agent_modifier<br/>- Tool context inspection<br/>- Directory listing capture"]
        BEFORE_MODEL["before_model_modifier<br/>- LLM request modification<br/>- Worktree context injection"]
    end

    subgraph Telemetry["Telemetry & Tracing"]
        OPIK["Opik Tracer<br/>- Agent execution tracking<br/>- track_adk_agent_recursive"]
        OPENINFERENCE["OpenInference<br/>(Commented)<br/>- Google ADK instrumentation"]
        LANGFUSE["Langfuse<br/>(Commented)<br/>- LLM observability"]
    end

    subgraph DataFlow["Planner Data Flow"]
        INSIGHTS["repo_insights<br/>README, AGENTS.md analysis"]
        FILES["files_to_modify<br/>File paths, dependencies"]
        IMPL_PLAN["implementation_plan<br/>Detailed tasks & code"]
        REVISED["revised_plan<br/>Finalized plan with feedback"]
    end

    ENV --> MODEL
    LITELLM --> MODEL
    GEMINI --> MODEL
    MODEL --> ROOT

    ROOT --> DEVELOPER
    ROOT --> PLANNER_ROOT

    PLANNER_ROOT --> SEQ

    SEQ --> REPO
    SEQ --> CHANGE_PLAN
    SEQ --> PLAN_WRITE
    SEQ --> REVISOR

    REPO --> REPO_TOOLS
    REVISOR --> REVISOR_TOOLS

    REPO -.-> INSIGHTS
    INSIGHTS -.-> CHANGE_PLAN
    CHANGE_PLAN -.-> FILES
    FILES -.-> PLAN_WRITE
    PLAN_WRITE -.-> IMPL_PLAN
    IMPL_PLAN -.-> REVISOR
    REVISOR -.-> REVISED

    DEVELOPER --> FILESYSTEM
    DEVELOPER --> READONLY_FS
    DEVELOPER --> SHELL

    DEVELOPER --> BEFORE_AGENT
    DEVELOPER --> BEFORE_MODEL

    ROOT --> OPIK
    PLANNER_ROOT --> OPIK
    DEVELOPER --> OPIK

    DEVELOPER --> OPENINFERENCE
    DEVELOPER --> LANGFUSE

    style ROOT fill:#ff6b6b,stroke:#c92a2a,color:#fff
    style PLANNER_ROOT fill:#ffd93d,stroke:#ffb700,color:#000
    style DEVELOPER fill:#4ecdc4,stroke:#0a9396,color:#fff
    style SEQ fill:#ffd93d,stroke:#ffb700,color:#000
    style REPO fill:#ffc145,stroke:#ffb700,color:#000
    style CHANGE_PLAN fill:#ffc145,stroke:#ffb700,color:#000
    style PLAN_WRITE fill:#ffc145,stroke:#ffb700,color:#000
    style REVISOR fill:#ffc145,stroke:#ffb700,color:#000
    style OPIK fill:#9b59b6,stroke:#8e44ad,color:#fff
    style CONFIG fill:#3498db,stroke:#2980b9,color:#fff
    style DataFlow fill:#f0f0f0,stroke:#999,color:#000
```

### Agent Workflow

#### Root Agent Layer
- **Root Agent** (`developer_agent`): Primary entry point for implementing code

#### Developer Agent
- Executes filesystem operations and shell commands
- Uses `filesystem_toolset` for file/directory creation and modification
- Uses `run_shell_command` for testing and validation
- Applies callback modifiers for context injection

#### Planner Agent (Sequential Workflow)
The PlannerAgent orchestrates a multi-stage planning process through a SequentialAgent:

1. **repo_agent** → Analyzes repository structure
   - Tools: Filesystem inspection (read_text_file, list_directory, directory_tree)
   - Output: `repo_insights` (README.md and AGENTS.md analysis)

2. **change_planner_agent** → Maps required changes
   - Input: repo_insights
   - Output: `files_to_modify` (file paths, dependencies, impact analysis)
   - No tools (analysis only)

3. **plan_writer_agent** → Creates detailed implementation plan
   - Input: files_to_modify
   - Output: `implementation_plan` (specific tasks, code snippets)
   - No tools (synthesis only)

4. **revisor_agent** → Validates and refines plan
   - Tools: Filesystem inspection (validate file paths and references)
   - Input: implementation_plan
   - Output: `revised_plan` (finalized with feedback and recommendations)

#### Bash Agent
- Validates work by running tests and service checks (currently commented)

### Callback Flow

1. **before_agent_modifier**: Captures worktree context before tool execution
2. **before_model_modifier**: Injects worktree context into LLM system instructions

### Telemetry

- **Opik**: Active tracing with `track_adk_agent_recursive()` for recursive agent monitoring
  - Tracks all agent executions (root, developer, planner, and sub-agents)
  - Logs metadata and performance metrics
- **OpenInference & Langfuse**: Available but commented out for debugging observability

## Getting Started

### Prerequisites

- Python 3.9 or higher
- `pip`

### Installation

1. Install dependencies:
   ```bash
   pip install -r doll_shop/requirements.txt
   ```

2. Run the server:
   ```bash
   uvicorn doll_shop.main:app --reload
   ```

3. Access the API documentation:
   - Interactive Swagger UI: `http://127.0.0.1:8000/docs`
   - ReDoc: `http://127.0.0.1:8000/redoc`

## API Endpoints

### Inventory
- `GET /dolls`: List all dolls. Optional `type` query parameter (`wooden`, `fluffed`, `electronic`).
- `POST /dolls`: Add a new doll.
- `GET /dolls/{doll_id}`: Get details of a specific doll.
- `PUT /dolls/{doll_id}`: Update doll details.
- `DELETE /dolls/{doll_id}`: Remove a doll.

### Reservations
- `POST /reservations`: Book a playtime slot.
- `GET /reservations`: View all reservations.
- `DELETE /reservations/{res_id}`: Cancel a reservation.

### Quick Check
- `GET /dolls/{doll_id}/price-check`: Get quick pricing and shipping info.
