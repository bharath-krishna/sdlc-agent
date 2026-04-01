# Doll Shop API

A FastAPI backend for a doll shop, providing CRUD operations for dolls, customers, and orders.

## Project Structure

```
/
├── pyproject.toml              # Project dependencies (managed by uv)
├── run.py                      # Uvicorn entry point
├── alembic.ini                 # Alembic configuration
├── conftest.py                 # Shared pytest fixtures
├── pytest.ini                  # Pytest configuration
├── api/
│   ├── main.py                 # FastAPI application and router registration
│   ├── configurations/         # Pydantic settings
│   ├── exceptions/             # Custom API exceptions
│   ├── models/                 # Pydantic request/response models
│   ├── modules/                # Business logic and database session management
│   ├── routers/                # FastAPI APIRouter definitions
│   └── schemas/                # SQLAlchemy ORM models
├── alembic/                    # Database migrations
├── terraform/                  # Terraform deployment configuration (Kubernetes)
└── tests/e2e/                  # End-to-end tests
```

## Getting Started

### Prerequisites

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) for package management
- PostgreSQL (or another supported database)

### Installation

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Set up environment variables (optional, defaults are in `api/configurations/base.py`):
   Create a `.env.local` file in the root:
   ```env
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   POSTGRES_USERNAME=postgres
   POSTGRES_PASSWORD=yourpassword
   POSTGRES_DB=dollshop
   API_SIGNATURE_TEXT=your_secret_key
   ```

### Database Migrations

1. Generate a migration:
   ```bash
   alembic revision --autogenerate -m "initial schema"
   ```

2. Apply migrations:
   ```bash
   alembic upgrade head
   ```

### Running the API

Start the server using the entry point:
```bash
python run.py
```
The API will be available at `http://localhost:9999/api`.
Interactive documentation (Swagger UI) is at `http://localhost:9999/docs`.

### Running with Docker

You can also run the application using Docker. The provided Dockerfile uses `uv` for efficient dependency management and includes an entrypoint script that automatically runs database migrations.

1. **Build the Docker image:**
   ```bash
   docker build -t doll-shop-api .
   ```

2. **Run the container:**
   ```bash
   docker run -p 9999:9999 --env-file .env doll-shop-api
   ```
   *Note: Ensure your `.env` file contains the correct database connection details accessible from within the Docker container.*

3. **How it works:**
   - The image is based on a slim Python 3.10 image.
   - It uses `uv` to install dependencies defined in `pyproject.toml`.
   - The `entrypoint.sh` script runs `alembic upgrade head` before starting the Uvicorn server.
   - The application is exposed on port `9999` (as configured in `run.py`).

## Deployment with Terraform

For automated infrastructure management, you can deploy the entire stack (API, Database, and Networking) to a Kubernetes cluster using Terraform.

1. **Navigate to the terraform directory**:
   ```bash
   cd terraform
   ```

2. **Initialize Terraform**:
   ```bash
   terraform init
   ```

3. **Configure Variables**:
   Create a `terraform.tfvars` file (do not commit this) and provide the required sensitive values:
   ```hcl
   postgres_password  = "your-secure-password"
   api_signature_text = "your-jwt-secret"
   ```

4. **Deploy**:
   ```bash
   terraform apply
   ```
   This provisions a namespace (`doll-shop`), PostgreSQL, the API (2 replicas), and an Ingress at `dollshop.krishb.in`.

## Running Tests

Run all tests:
```bash
pytest
```

Run tests for a specific feature:
```bash
pytest -m dolls
pytest -m customers
pytest -m orders
```

## Features

### Dolls
- `GET /api/dolls`: List all dolls.
- `GET /api/dolls/{id}`: Get details of a specific doll.
- `POST /api/dolls`: Add a new doll (Auth required).
- `PUT /api/dolls/{id}`: Update doll details (Auth required).
- `DELETE /api/dolls/{id}`: Remove a doll (Auth required).

### Customers
- `GET /api/customers`: List all customers (Auth required).
- `GET /api/customers/{id}`: Get customer details (Auth required).
- `POST /api/customers`: Register a new customer (Auth required).
- `PUT /api/customers/{id}`: Update customer profile (Auth required).
- `DELETE /api/customers/{id}`: Delete a customer record (Auth required).

### Orders
- `GET /api/orders`: List all orders (Auth required).
- `GET /api/orders/{id}`: Get order details (Auth required).
- `POST /api/orders`: Place a new order (Auth required). Handles stock validation and price calculation.
- `DELETE /api/orders/{id}`: Cancel/Delete an order (Auth required).

## Authentication

Authenticated endpoints require a Bearer token in the `Authorization` header.
Tokens are HS256 signed JWTs containing user identity information.
