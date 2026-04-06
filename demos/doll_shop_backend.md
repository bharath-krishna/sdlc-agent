# Backend Development Guide

## Overview

Complete instructions for SWE agents to develop FastAPI backends following this repository's architecture using `uv` for dependency management.

## Guide Contents

### ✅ Project Setup

Initial configuration and dependencies using `uv init`

**🔥 Critical First Steps:**
1. Run `uv init` to bootstrap the project
2. **Immediately run `git init` and make first commit** — Don't skip this step
3. Set up your `.gitignore` file
4. Continue with dependencies and configuration

### ✅ Version Control Best Practices

- Initialize git right after project creation
- Commit after each completed feature implementation
- Use descriptive commit messages (e.g., `"Feature: Add customer CRUD endpoints"`)
- Commit at logical intervals to maintain clean history

### ✅ UV Project Initialization

Scripts and steps to initialize projects with `uv`:

- `uv init` project structure
- **⚠️ Initialize git immediately after `uv init`** — Run `git init` and commit initial state
- Managing dependencies with `uv`
- Creating and running scripts
- **Commit frequently** — After each feature implementation or at logical intervals

### ✅ Architecture Overview

Layered structure explanation:

- Routers → Modules → Schemas → Models

### ✅ Development Workflow

Step-by-step guide to create new features:

1. Create ORM schema
2. Create Pydantic models
3. Create module (business logic)
4. Create router (HTTP endpoints)
5. Register router
6. Create migrations
7. **✅ Commit** — After each feature is complete, run `git add -A && git commit -m "Feature: <description>"`
   - Helps track progress and enable rollbacks
   - Maintains clean history for code review

### ✅ Database & ORM

SQLAlchemy async patterns and query examples

### ✅ Authentication

JWT setup and usage

### ✅ Testing

E2E testing with CustomClient

### ✅ Error Handling

Custom APIError class and usage

### ✅ Configuration

Settings management and environment variables

### ✅ Docker & Deployment

Dockerfile and docker-compose setup

### ✅ Code Patterns & Conventions

- Naming conventions
- Async/await patterns
- Type hints
- Docstrings

### ✅ Common Tasks

- How to add endpoints
- How to check auth
- How to query DB

### ✅ Troubleshooting

Solutions for common issues

## Included Resources

- 50+ code examples showing real patterns
- Quick reference tables for status codes, env vars, and routes
- Complete workflow from schema to deployment
- Testing patterns with CustomClient
- Error handling best practices
- `uv` initialization and script management examples

Build a doll shop backend apis including crud operations for common features, like listing/filtering dolls based on price, category, material, size, weight etc.

order placemement, purchase history of the user, user filtering (include common user/customer details).
