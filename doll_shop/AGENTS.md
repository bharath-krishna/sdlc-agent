# Doll Shop API - Agent Guide

This document provides an overview of the Doll Shop API project for AI agents and developers. It details the project structure, technical stack, and operational procedures.

## Project Overview

The Doll Shop API is a FastAPI-based backend providing CRUD operations for a doll shop, including management of dolls, customers, orders, and reservations. It uses SQLAlchemy (with `asyncpg`) for database interactions and Alembic for migrations.

## Repository Structure

```text
doll_shop/
├── AGENTS.md                   # This file (Agent & Developer guide)
├── README.md                   # General project documentation
├── pyproject.toml              # Project metadata and dependencies (managed by uv)
├── uv.lock                     # Locked versions of dependencies
├── run.py                      # Uvicorn entry point (Application runner)
├── alembic.ini                 # Alembic configuration for migrations
├── conftest.py                 # Shared pytest fixtures
├── pytest.ini                  # Pytest configuration
├── .dockerignore               # Files excluded from Docker builds
├── Dockerfile                  # Container definition (Multi-stage with uv)
├── entrypoint.sh               # Container startup script (Migrations + Run)
├── .env                        # Local environment variables (do not commit sensitive data)
├── api/                        # Core application code
│   ├── main.py                 # FastAPI application and router registration
│   ├── configurations/         # Pydantic settings and environment config
│   ├── exceptions/             # Custom API exceptions
│   ├── models/                 # Pydantic request/response models
│   ├── modules/                # Business logic and DB session management
│   ├── routers/                # FastAPI APIRouter definitions
│   └── schemas/                # SQLAlchemy ORM models
├── alembic/                    # Database migration scripts and versions
├── k8s/                        # Kubernetes manifests (Kustomize)
│   ├── base/                   # Core K8s resources (Deployment, Service, ConfigMap, Ingress)
│   └── overlays/production/    # Production-specific overrides and Secrets
├── terraform/                  # Terraform configuration for K8s deployment
├── tests/                      # Test suite
│   └── e2e/                    # End-to-end tests
└── docs/                       # Project documentation files
```

## Technical Stack

- **Framework**: FastAPI
- **Python Version**: 3.10+
- **Package Manager**: [uv](https://github.com/astral-sh/uv)
- **Database**: PostgreSQL (via `sqlalchemy` and `asyncpg` for async, `psycopg2` for sync migrations)
- **Migrations**: Alembic
- **Testing**: Pytest
- **Containerization**: Docker (optimized with `uv` caching)
- **Orchestration**: Kubernetes with Kustomize

## Development Workflow

### Environment Setup

1.  **Sync Dependencies**: `uv sync` (creates/updates `.venv`)
2.  **Environment Variables**: Configured in `api/configurations/base.py`. Use a `.env.local` or `.env` file for overrides.
    - `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`
    - `POSTGRES_USERNAME`, `POSTGRES_PASSWORD`
    - `API_SIGNATURE_TEXT` (JWT signing key)

### Core Commands

| Action | Command |
| :--- | :--- |
| **Start API** | `uv run python run.py` |
| **Run Tests** | `uv run pytest` |
| **Migrations** | `uv run alembic upgrade head` |
| **New Migration** | `uv run alembic revision --autogenerate -m "message"` |

## Deployment

### Docker

- **Build**: `docker build -t doll-shop-api ./doll_shop`
- **Run**: `docker run -p 9999:9999 --env-file .env doll-shop-api`
- **Note**: The image uses an `ENTRYPOINT` script that automatically runs migrations before starting the server.

### Kubernetes (Kustomize)

- **Structure**: `k8s/base` defines the application; `k8s/overlays/production` handles secrets and image tagging.
- **Endpoint**: Configured for `dollshop.krishb.in` via Ingress.
- **Preview**: `kubectl kustomize doll_shop/k8s/overlays/production`
- **Deploy**: `kubectl apply -k doll_shop/k8s/overlays/production`

### Terraform

The application can be deployed via Terraform to manage Kubernetes resources (Namespace, Deployments, Services, Secrets, and Ingress) as stateful objects.

- **Location**: `doll_shop/terraform/`
- **Variables**: Managed via `variables.tf`. Sensitive inputs (`postgres_password`, `api_signature_text`) must be provided via `terraform.tfvars` or environment variables.
- **Workflow**: `terraform init` -> `terraform plan` -> `terraform apply`.

## Coding Guidelines

- **API Responses**: Use Pydantic models from `api/models/` for consistent schema responses.
- **Business Logic**: Keep routers thin; place logic in `api/modules/`.
- **Database**: Use async sessions for API endpoints; ensure migrations are generated for every schema change.
