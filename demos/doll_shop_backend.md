# Backend Development Guide

## Overview

Complete instructions for SWE agents to develop FastAPI backends following this repository's architecture using `uv` for dependency management.

## 🔄 Core Development Workflow

Every iteration follows this pattern:

1. **Perform Incremental Progress** — Complete one small, focused feature or task
2. **Document Everything** — Update progress.md with what was done
3. **Write Progress Summary** — Document completed work and next steps
4. **Commit Changes** — Create a meaningful git commit with descriptive message
5. **Repeat** — Move to next feature in the backlog

This ensures steady progress, clean history, and easy rollbacks.

## Guide Contents

### ✅ Project Setup (Iteration 1)

Initial configuration and dependencies using `uv init`

**🔥 Critical First Steps:**

1. Run `uv init` to bootstrap the project
2. **Immediately run `git init` and make first commit** — Don't skip this step
3. Set up your `.gitignore` file
4. Continue with dependencies and configuration

**✅ After Setup — Document & Commit:**

- Create `progress.md` file and document: "Iteration 1: Project scaffolding complete. Initial `uv` and git setup done."
- Commit with message: `"Setup: Initialize project with uv and git"`
- Note next iteration: "Iteration 2: Add core dependencies and database configuration"

### ✅ Version Control Best Practices

- Initialize git right after project creation
- **Document in `progress.md` before each commit** — Track iteration number, what was completed, and next steps
- **Commit after each completed feature** — Following the 5-step workflow
- Use descriptive commit messages (e.g., `"Feature: Add customer CRUD endpoints"`)
- Commit at logical intervals to maintain clean history
- Each commit corresponds to one completed iteration

**Progress.md Format:**

```
## Iteration X: [Feature Name]
### Completed
- [Task 1]
- [Task 2]

### Next Iteration
- [Task 3]
- [Task 4]
```

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

### ✅ Development Workflow (Per Feature)

Each feature follows the **5-Step Iterative Workflow**:

#### Per-Feature Workflow:

1. Create ORM schema
2. Create Pydantic models
3. Create module (business logic)
4. Create router (HTTP endpoints)
5. Register router
6. Create migrations

#### Then: Apply the 5-Step Cycle (One per complete feature/endpoint)

**Step 1: Perform Incremental Progress**

- Implement one focused feature (e.g., "Add doll listing endpoint")
- Keep scope small and testable

**Step 2: Document Everything**

- Update function docstrings
- Add type hints
- Document any new database changes
- Write test cases if applicable

**Step 3: Write Progress Summary**

- Update `progress.md` with the current iteration number and feature
- List what was completed
- List what needs to be done next
- Example:

  ```
  ## Iteration 2: Add Doll Listing Endpoint
  ### Completed
  - Created DollSchema ORM model
  - Created DollResponse Pydantic model
  - Implemented get_dolls() business logic with filtering
  - Added GET /dolls router endpoint
  - Registered router in main.py

  ### Next Iteration
  - Add doll creation endpoint (POST /dolls)
  - Add doll update endpoint (PATCH /dolls/{id})
  ```

**Step 4: Commit Changes**

- Stage changes: `git add -A`
- Commit with descriptive message: `git commit -m "Feature: Add doll listing endpoint with filtering"`
- Message format: `"[Type]: [What was done]"` (Feature, Fix, Refactor, Docs, etc.)

**Step 5: Repeat**

- Move to next feature in backlog
- Each feature = one iteration = one commit

**Why This Works:**

- Helps track progress and enable rollbacks
- Maintains clean, readable git history
- Easy to review and understand what changed when
- Progress.md serves as living documentation
- Each commit represents one logical unit of work

### ✅ Database & ORM

SQLAlchemy async patterns and query examples

#### PostgreSQL Database Setup

For development and testing, use the shared PostgreSQL database:

**Database Connection Details:**

- **Host:** `pg.krishb.in`
- **Port:** `5432`
- **Username:** `postgres`
- **SSL Mode:** `disable`

**Get PostgreSQL Password:**

```bash
export POSTGRES_PASSWORD=$(kubectl get secret --namespace postgresql postgresql -o jsonpath="{.data.postgres-password}" | base64 -d)
```

**Connect to PostgreSQL via psql:**

```bash
psql "host=pg.krishb.in port=5432 user=postgres sslmode=disable password=$POSTGRES_PASSWORD"
```

**Backend Environment Configuration:**

Set these environment variables in your `.env` file:

```env
DATABASE_URL=postgresql+asyncpg://postgres:${POSTGRES_PASSWORD}@pg.krishb.in:5432/doll_shop
```

Or directly in your configuration:

```env
DATABASE_HOST=pg.krishb.in
DATABASE_PORT=5432
DATABASE_USER=postgres
DATABASE_PASSWORD=${POSTGRES_PASSWORD}
DATABASE_NAME=doll_shop
```

**Example SQLAlchemy Configuration:**

```python
from sqlalchemy.ext.asyncio import create_async_engine
import os

# Get password from environment
db_password = os.getenv('POSTGRES_PASSWORD')
DATABASE_URL = f"postgresql+asyncpg://postgres:{db_password}@pg.krishb.in:5432/doll_shop"

engine = create_async_engine(DATABASE_URL, echo=False)
```

**Create Database:**

```bash
# First, get the password
export POSTGRES_PASSWORD=$(kubectl get secret --namespace postgresql postgresql -o jsonpath="{.data.postgres-password}" | base64 -d)

# Create the database
createdb -h pg.krishb.in -U postgres -p 5432 doll_shop
```

**Running Alembic Migrations:**

After setting up your database, run migrations with:

```bash
# Get the password
export POSTGRES_PASSWORD=$(kubectl get secret --namespace postgresql postgresql -o jsonpath="{.data.postgres-password}" | base64 -d)

# Run migrations
SQLALCHEMY_DATABASE_URL="postgresql+asyncpg://postgres:${POSTGRES_PASSWORD}@pg.krishb.in:5432/doll_shop" alembic upgrade head
```

**⚠️ Important Notes:**

- Always retrieve the password fresh before connecting — it's stored in Kubernetes secrets
- Each developer can use the same shared database for development
- Create separate test databases for testing (e.g., `doll_shop_test`)
- Store the password in `.env` file (add `.env` to `.gitignore`) for local development

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

#### Dockerfile

Create `Dockerfile` in the project root:

```dockerfile
# Use official Python runtime as base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Copy project files
COPY pyproject.toml uv.lock* ./

# Install Python dependencies
RUN uv sync --frozen

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Run the application
CMD ["uv", "run", "python", "-m", "api.main"]
```

#### Docker Compose Setup

Create `docker-compose.yml` in the project root:

```yaml
version: "3.9"

services:
  # FastAPI Backend Service
  api:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: doll_shop_api
    ports:
      - "8000:8000"
    environment:
      - DATABASE_HOST=pg.krishb.in
      - DATABASE_PORT=5432
      - DATABASE_USER=postgres
      - DATABASE_NAME=doll_shop
      - DATABASE_PASSWORD=${POSTGRES_PASSWORD}
      - PYTHONUNBUFFERED=1
    depends_on:
      - db # Optional: if using local PostgreSQL for testing
    volumes:
      - .:/app
    networks:
      - doll_shop_network
    command: uv run uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

  # Optional: Local PostgreSQL for testing (remove if using remote pg.krishb.in only)
  db:
    image: postgres:16-alpine
    container_name: doll_shop_postgres
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-postgres}
      - POSTGRES_DB=doll_shop_test
    ports:
      - "5433:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - doll_shop_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

networks:
  doll_shop_network:
    driver: bridge

volumes:
  postgres_data:
```

#### Build and Run with Docker Compose

**1. Set the PostgreSQL password:**

```bash
export POSTGRES_PASSWORD=$(kubectl get secret --namespace postgresql postgresql -o jsonpath="{.data.postgres-password}" | base64 -d)
```

**2. Build the Docker image:**

```bash
docker-compose build
```

**3. Start the services:**

```bash
docker-compose up -d
```

**4. Check logs:**

```bash
docker-compose logs -f api
```

**5. Stop the services:**

```bash
docker-compose down
```

**6. Stop services and remove volumes:**

```bash
docker-compose down -v
```

#### Running Migrations in Docker

**Create a migration service in docker-compose.yml** (optional):

```yaml
migrate:
  build:
    context: .
    dockerfile: Dockerfile
  container_name: doll_shop_migrate
  environment:
    - DATABASE_HOST=pg.krishb.in
    - DATABASE_PORT=5432
    - DATABASE_USER=postgres
    - DATABASE_NAME=doll_shop
    - DATABASE_PASSWORD=${POSTGRES_PASSWORD}
  depends_on:
    - api
  networks:
    - doll_shop_network
  command: uv run alembic upgrade head
```

**Or run migrations manually:**

```bash
docker-compose exec api uv run alembic upgrade head
```

#### .dockerignore

Create `.dockerignore` in the project root:

```
.git
.gitignore
.env
.env.local
.venv
venv
__pycache__
*.pyc
*.pyo
*.pyd
.Python
.pytest_cache
.coverage
htmlcov
dist
build
*.egg-info
.DS_Store
node_modules
.idea
.vscode
*.swp
*.swo
.docker
```

#### Environment Configuration

**For development with remote PostgreSQL (pg.krishb.in):**

Create `.env` file (add to `.gitignore`):

```env
POSTGRES_PASSWORD=<your-password-from-kubectl>
DATABASE_HOST=pg.krishb.in
DATABASE_PORT=5432
DATABASE_USER=postgres
DATABASE_NAME=doll_shop
```

**For testing with local PostgreSQL:**

```env
POSTGRES_PASSWORD=test_password
DATABASE_HOST=localhost
DATABASE_PORT=5433
DATABASE_USER=postgres
DATABASE_NAME=doll_shop_test
```

#### Useful Docker Commands

| Command                        | Purpose                           |
| ------------------------------ | --------------------------------- |
| `docker-compose build`         | Build Docker image                |
| `docker-compose up -d`         | Start services in background      |
| `docker-compose down`          | Stop and remove containers        |
| `docker-compose logs -f api`   | View API logs in real-time        |
| `docker-compose exec api bash` | Open shell in running container   |
| `docker-compose ps`            | List running containers           |
| `docker image ls`              | List built images                 |
| `docker system prune`          | Clean up unused images/containers |

#### Tips for Development

✅ **Hot Reload:** The compose file includes `volumes: - .:/app` for hot reload during development
✅ **Separate Test Database:** Use local PostgreSQL for testing, remote for development
✅ **Environment Isolation:** Keep `.env` in `.gitignore` to prevent credential leaks
✅ **Health Checks:** API includes health check endpoint for Docker to monitor service status
✅ **Network:** All services use `doll_shop_network` for inter-service communication

#### Kubernetes Deployment with Kustomize

Deploy to Kubernetes using Kustomize for managing base and environment-specific overlays.

**Directory Structure:**

```
k8s/
├── base/
│   ├── kustomization.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── configmap.yaml
│   └── namespace.yaml
└── overlays/
    └── local/
        ├── kustomization.yaml
        ├── deployment-patch.yaml
        └── configmap-patch.yaml
```

**Base Configuration Files:**

**1. k8s/base/namespace.yaml**

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: doll-shop
```

**2. k8s/base/deployment.yaml**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: doll-shop-api
  namespace: doll-shop
  labels:
    app: doll-shop-api
    version: v1
spec:
  replicas: 2
  selector:
    matchLabels:
      app: doll-shop-api
  template:
    metadata:
      labels:
        app: doll-shop-api
        version: v1
    spec:
      containers:
        - name: api
          image: doll-shop-api:latest
          imagePullPolicy: IfNotPresent
          ports:
            - name: http
              containerPort: 8000
              protocol: TCP
          env:
            - name: DATABASE_HOST
              valueFrom:
                configMapKeyRef:
                  name: doll-shop-config
                  key: database_host
            - name: DATABASE_PORT
              valueFrom:
                configMapKeyRef:
                  name: doll-shop-config
                  key: database_port
            - name: DATABASE_USER
              valueFrom:
                configMapKeyRef:
                  name: doll-shop-config
                  key: database_user
            - name: DATABASE_NAME
              valueFrom:
                configMapKeyRef:
                  name: doll-shop-config
                  key: database_name
            - name: DATABASE_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: doll-shop-secrets
                  key: postgres_password
            - name: PYTHONUNBUFFERED
              value: "1"
            - name: PYTHONDONTWRITEBYTECODE
              value: "1"
          livenessProbe:
            httpGet:
              path: /health
              port: http
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /health
              port: http
            initialDelaySeconds: 5
            periodSeconds: 5
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 500m
              memory: 512Mi
```

**3. k8s/base/service.yaml**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: doll-shop-api
  namespace: doll-shop
  labels:
    app: doll-shop-api
spec:
  type: ClusterIP
  selector:
    app: doll-shop-api
  ports:
    - name: http
      port: 8000
      targetPort: 8000
      protocol: TCP
```

**4. k8s/base/configmap.yaml**

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: doll-shop-config
  namespace: doll-shop
data:
  database_host: "pg.krishb.in"
  database_port: "5432"
  database_user: "postgres"
  database_name: "doll_shop"
```

**5. k8s/base/kustomization.yaml**

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

namespace: doll-shop

resources:
  - namespace.yaml
  - deployment.yaml
  - service.yaml
  - configmap.yaml

commonLabels:
  app: doll-shop-api
  project: doll-shop

commonAnnotations:
  managed-by: kustomize
```

**Local Overlay Configuration:**

**1. k8s/overlays/local/kustomization.yaml**

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

bases:
  - ../../base

namespace: doll-shop

replicas:
  - name: doll-shop-api
    count: 1

patchesStrategicMerge:
  - deployment-patch.yaml

patchesJson6902:
  - target:
      group: v1
      version: v1
      kind: ConfigMap
      name: doll-shop-config
    patch: |-
      - op: replace
        path: /data/database_host
        value: "localhost"
      - op: replace
        path: /data/database_port
        value: "5433"

secretGenerator:
  - name: doll-shop-secrets
    behavior: merge
    literals:
      - postgres_password=${POSTGRES_PASSWORD}

namePrefix: local-
nameSuffix: -dev
```

**2. k8s/overlays/local/deployment-patch.yaml**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: doll-shop-api
spec:
  replicas: 1
  template:
    spec:
      containers:
        - name: api
          image: doll-shop-api:local
          imagePullPolicy: Never
          resources:
            requests:
              cpu: 50m
              memory: 64Mi
            limits:
              cpu: 250m
              memory: 256Mi
```

**Using Kustomize for Deployment:**

**1. Build and view the manifest:**

```bash
# View the generated Kubernetes manifest
kubectl kustomize k8s/overlays/local/

# Or build to a file
kubectl kustomize k8s/overlays/local/ > manifest.yaml
```

**2. Set up secrets before deploying:**

```bash
# Get the password from Kubernetes
export POSTGRES_PASSWORD=$(kubectl get secret --namespace postgresql postgresql -o jsonpath="{.data.postgres-password}" | base64 -d)

# Verify it's set
echo $POSTGRES_PASSWORD
```

**3. Deploy to local Kubernetes cluster:**

```bash
# First, ensure the Docker image is built
docker build -t doll-shop-api:local .

# Load image into local Kubernetes (for kind or minikube)
kind load docker-image doll-shop-api:local
# OR for minikube:
eval $(minikube docker-env)
docker build -t doll-shop-api:local .

# Apply the Kustomize configuration
kubectl apply -k k8s/overlays/local/
```

**4. Verify the deployment:**

```bash
# Check deployments
kubectl get deployments -n doll-shop

# Check pods
kubectl get pods -n doll-shop

# Check services
kubectl get svc -n doll-shop

# View logs
kubectl logs -n doll-shop -l app=doll-shop-api -f

# Port forward to access locally
kubectl port-forward -n doll-shop svc/local-doll-shop-api-dev 8000:8000
```

**5. Clean up:**

```bash
# Delete the deployment
kubectl delete -k k8s/overlays/local/

# Or delete the namespace (removes everything)
kubectl delete namespace doll-shop
```

**Useful Kustomize Commands:**

| Command                                 | Purpose                                 |
| --------------------------------------- | --------------------------------------- |
| `kubectl kustomize k8s/overlays/local/` | View generated manifest                 |
| `kubectl apply -k k8s/overlays/local/`  | Deploy using Kustomize                  |
| `kubectl diff -k k8s/overlays/local/`   | Show what would change                  |
| `kubectl delete -k k8s/overlays/local/` | Delete deployment                       |
| `kustomize build k8s/overlays/local/`   | Build manifest (requires kustomize CLI) |

**Creating Additional Overlays:**

For production deployment, create `k8s/overlays/production/`:

```yaml
# k8s/overlays/production/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

bases:
  - ../../base

replicas:
  - name: doll-shop-api
    count: 3

patchesStrategicMerge:
  - deployment-patch.yaml

# Use sealed-secrets or external-secrets for production
secretGenerator:
  - name: doll-shop-secrets
    behavior: merge
    envs:
      - secrets.env

# Add ingress for production
resources:
  - ingress.yaml
```

**Tips for Kustomize Development:**

✅ **Base for shared configs** — Keep base lean with common settings
✅ **Overlays for environments** — Customize per environment (local, staging, production)
✅ **Use patches wisely** — Strategic merge for simple changes, JSON patches for complex ones
✅ **Name prefixes/suffixes** — Helps distinguish resources across environments
✅ **Secret management** — Use kustomize's secretGenerator or external-secrets for production
✅ **Resource limits** — Set appropriate CPU/memory for each environment
✅ **Version control** — Commit k8s/ directory for tracking infrastructure changes

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

## 📋 Project Backlog: Doll Shop Backend

Build a doll shop backend APIs including CRUD operations for common features:

### Doll Management

- List/filter dolls (price, category, material, size, weight, etc.)
- Create doll listing
- Update doll details
- Delete doll

### Customer Management

- User registration
- User profile (common user/customer details)
- User filtering and search

### Order Management

- Order placement
- Purchase history per user
- Order status tracking
- Order cancellation

### Implementation: Iterative Approach

**Suggested Iteration Order:**

1. Iteration 1: Project setup with uv and git
2. Iteration 2: Database + ORM setup (SQLAlchemy, Alembic)
3. Iteration 3: Doll model and GET /dolls endpoint
4. Iteration 4: Doll filtering and search
5. Iteration 5: Create doll endpoint (POST)
6. Iteration 6: Update doll endpoint (PATCH)
7. Iteration 7: Customer model and endpoints
8. Iteration 8: Authentication (JWT)
9. Iteration 9: Order model and endpoints
10. Iteration 10: Order history and filtering

Each iteration = one commit with progress.md updated.

## ✅ Iteration Tracking Template

Create a `progress.md` file at project root with this structure:

```markdown
# Project Progress

## Iteration 1: Project Setup

### Completed

- Initialized project with `uv init`
- Created git repository and made first commit
- Set up .gitignore

### Next Iteration

- Add FastAPI and database dependencies
- Configure SQLAlchemy and Alembic

---

## Iteration 2: Database & ORM Setup

### Completed

- [Describe work here]

### Next Iteration

- [Describe next work here]

---
```
