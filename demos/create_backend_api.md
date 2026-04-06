# Create a New FastAPI Backend API

This document instructs an AI agent how to scaffold a new feature API in this
repository. Follow every step exactly. Do not skip steps, do not invent new
patterns. All paths below are relative to the repository root.

---

## Repository Tree

```
/
├── pyproject.toml              # uv-managed project deps
├── run.py                      # uvicorn entry point
├── alembic.ini                 # Alembic config (sqlalchemy.url overridden in env.py)
├── conftest.py                 # registers shared pytest fixtures
├── pytest.ini                  # pytest config, markers
├── .env.local                  # local env overrides (gitignored)
├── api/
│   ├── main.py                 # FastAPI app factory + router registration
│   ├── configurations/
│   │   ├── __init__.py
│   │   └── base.py             # Settings (pydantic-settings), config singleton
│   ├── exceptions/
│   │   ├── __init__.py
│   │   └── api.py              # APIError(HTTPException), ErrorMessages dict
│   ├── middlewares/
│   │   └── __init__.py
│   ├── models/                 # Pydantic request/response shapes
│   │   ├── __init__.py
│   │   ├── auth.py             # require_user JWT dependency
│   │   ├── profile.py          # UserModel
│   │   └── cats.py             # CatModel, InquiryModel, OrderModel, PlaytimeModel
│   ├── modules/                # Business logic
│   │   ├── __init__.py         # BaseModule(request, db)
│   │   ├── database.py         # engine, get_db, Base
│   │   ├── profile.py          # ProfileModule
│   │   └── cats.py             # CatsModule
│   ├── routers/                # FastAPI APIRouter definitions
│   │   ├── __init__.py
│   │   ├── profile.py          # /profile routes
│   │   └── cats.py             # /cats, /inquiries, /orders, /playtime routes
│   └── schemas/                # SQLAlchemy ORM table models
│       ├── __init__.py
│       └── cats.py             # Cat, Inquiry, Order, PlaytimeReservation
├── alembic/
│   ├── env.py                  # imports Base + all schemas, sets sqlalchemy.url
│   ├── script.py.mako
│   └── versions/               # migration files (e.g. 0001_initial_cats_schema.py)
├── tests/e2e/
│   ├── __init__.py             # CustomClient, MockUser
│   ├── conftest.py
│   ├── conf/
│   │   ├── __init__.py
│   │   ├── _conftest_auth.py   # mock_user, mock_user_token, user_client fixtures
│   │   └── _conftest_common.py # function_client fixture
│   └── profile/
│       ├── __init__.py
│       └── test_profile.py     # example e2e test
├── docs/
│   ├── alembic.md
│   └── database.md
└── demos/
    └── create_backend_api.md   # this file
```

---

## Package Management with uv

This project uses [uv](https://github.com/astral-sh/uv) to manage dependencies.
Do not use pip directly. Do not use pipenv. Use `uv` for all dependency operations.

### Add a runtime dependency

```bash
uv add <package-name>
```

Example — add aiosqlite for SQLite local dev:

```bash
uv add aiosqlite
```

### Add a dev/test-only dependency

```bash
uv add --dev <package-name>
```

### Remove a dependency

```bash
uv remove <package-name>
```

### Install all dependencies (sync from uv.lock)

```bash
uv sync
```

### pyproject.toml structure

Dependencies live in `pyproject.toml` under `[project].dependencies`. The
current set is:

```toml
[project]
name = "kittykat-apis"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "fastapi",
    "uvicorn[standard]",
    "pyjwt[crypto]",
    "pydantic-settings",
    "python-dotenv",
    "pytest",
    "pytest-cov",
    "requests",
    "sqlalchemy[asyncio]",
    "asyncpg",
    "alembic",
    "psycopg2-binary",
]
```

After running `uv add` or `uv remove`, both `pyproject.toml` and `uv.lock`
are updated automatically. **Commit both files immediately:**

```bash
git add pyproject.toml uv.lock
git commit -m "chore: update dependencies with uv add <package>"
```

---

## Version Control Setup

**🔥 Initialize git immediately after creating the project:**

```bash
# After creating your project and running initial setup
git init
git add -A
git commit -m "Initial project setup with uv dependencies"
```

This establishes your project history before any development begins. Do not skip this step.

---

## Environment Setup

The application uses `python-dotenv` to load environment variables from a `.env.local`
file at the project root. This file is gitignored and contains local development settings.

### Create `.env.local`

Create a `.env.local` file at the repository root with the following environment
variables. Adjust values as needed for your local setup:

```bash
# .env.local (do not commit this file)

# FastAPI configuration
API_PREFIX=/api
API_HOST=0.0.0.0
API_PORT=8088
API_SIGNATURE_TEXT=somesecret
API_WORKERS=4
API_RELOAD=True
API_ACCESS_LOG=True
API_DEBUG=True

# PostgreSQL configuration (no API_ prefix required for these)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USERNAME=postgres
POSTGRES_PASSWORD=yourpassword
POSTGRES_DB=kittykat
```

### How Environment Variables Are Loaded

Environment variables are automatically loaded by `pydantic-settings` in
`api/configurations/base.py`. The `Settings` class reads from:

1. OS environment variables
2. `.env.local` file (if it exists)
3. Default values defined in the Settings class

Variables with the `API_` prefix are read via `env_prefix="API_"`. PostgreSQL
variables (POSTGRES\_\*) use `validation_alias` to bypass the prefix.

### Running the Development Server

Start the server with:

```bash
python run.py
```

The server will start with default host and port from `.env.local` (or config
defaults). To override host/port at runtime:

```bash
python run.py --host 127.0.0.1 --port 9000
```

The server runs with:

- `reload=True` — hot reload on file changes
- `workers=1` — single worker for local development
- All configuration loaded from `.env.local`

---

## Project Layout — Where Each Piece Lives

| What                       | Where                                   | Naming convention                  |
| -------------------------- | --------------------------------------- | ---------------------------------- |
| SQLAlchemy ORM table model | `api/schemas/<feature>.py`              | `class Widget(Base)`               |
| Pydantic request model     | `api/models/<feature>.py`               | `class WidgetRequest(BaseModel)`   |
| Pydantic response model    | `api/models/<feature>.py`               | `class WidgetModel(BaseModel)`     |
| Business logic             | `api/modules/<feature>.py`              | `class WidgetsModule(BaseModule)`  |
| Route handlers             | `api/routers/<feature>.py`              | `router = APIRouter()`             |
| Error keys                 | `api/exceptions/api.py`                 | Add to `ErrorMessages.ERRORS` dict |
| App config vars            | `api/configurations/base.py`            | Field on `Settings`                |
| Migrations                 | `alembic/versions/`                     | `NNNN_description.py`              |
| e2e tests                  | `tests/e2e/<feature>/test_<feature>.py` | `def test_<action>(user_client)`   |

One file per feature domain across all layers. If you are adding a "widgets"
feature, create exactly these five files:

1. `api/schemas/widgets.py`
2. `api/models/widgets.py`
3. `api/modules/widgets.py`
4. `api/routers/widgets.py`
5. `tests/e2e/widgets/test_widgets.py`

Then modify two existing files:

- `api/main.py` — import and register the new router
- `alembic/env.py` — import the new schema module

---

## Step-by-Step: Adding a New API Feature

Use `cats` as the concrete reference implementation throughout. Replace `cats` /
`Cat` / `CatsModule` with your feature name at every step.

### Step 1 — Create the SQLAlchemy schema (`api/schemas/<feature>.py`)

Inherit from `Base` imported from `api.modules.database`. Use `String` PKs with
`uuid.uuid4()` defaults. All tables must follow this pattern exactly:

```python
# api/schemas/widgets.py
import uuid
from sqlalchemy import String, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column
from api.modules.database import Base


class Widget(Base):
    __tablename__ = "widgets"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
```

Add ForeignKey columns and `relationship()` as needed, following the pattern
in `api/schemas/cats.py`.

### Step 2 — Create the Pydantic models (`api/models/<feature>.py`)

Define one request model per write operation and one response model per
resource. Every response model MUST include `model_config = ConfigDict(from_attributes=True)`
so SQLAlchemy ORM objects can be serialized directly.

```python
# api/models/widgets.py
from pydantic import BaseModel, ConfigDict


class WidgetRequest(BaseModel):
    name: str
    description: str
    quantity: int


class WidgetModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: str
    quantity: int
```

Do not add `model_config` to request-only models (e.g. `WidgetRequest`) — they
receive plain JSON dicts, not ORM objects.

### Step 3 — Create the module (`api/modules/<feature>.py`)

Extend `BaseModule` from `api.modules`. Access the async DB session via
`self.db`. Access the raw FastAPI `Request` via `self.request`. Keep all DB
queries here — never put `select()` statements in routers.

```python
# api/modules/widgets.py
from sqlalchemy import select
from api.modules import BaseModule
from api.exceptions.api import APIError
from api.schemas.widgets import Widget


class WidgetsModule(BaseModule):

    async def list_widgets(self):
        result = await self.db.execute(select(Widget))
        return result.scalars().all()

    async def get_widget(self, widget_id: str):
        result = await self.db.execute(
            select(Widget).where(Widget.id == widget_id)
        )
        widget = result.scalar_one_or_none()
        if not widget:
            raise APIError("not_found", field="widget_id", value=widget_id)
        return widget

    async def create_widget(self, body):
        widget = Widget(
            name=body.name,
            description=body.description,
            quantity=body.quantity,
        )
        self.db.add(widget)
        await self.db.commit()
        await self.db.refresh(widget)
        return widget
```

The pattern for every write operation is: construct ORM instance, `self.db.add()`,
`await self.db.commit()`, `await self.db.refresh()`, return the instance.

### Step 4 — Create the router (`api/routers/<feature>.py`)

Import `APIRouter`, `Depends`, `Request` from `fastapi`. Import `get_db` from
`api.modules.database`. Import `require_user` from `api.models.auth` when the
route needs authentication. Instantiate the module inside each handler — never
store module state outside a handler function.

```python
# api/routers/widgets.py
from typing import List
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from api.modules.widgets import WidgetsModule
from api.modules.database import get_db
from api.models.auth import require_user
from api.models.widgets import WidgetRequest, WidgetModel

router = APIRouter()


@router.get(
    '/widgets',
    tags=['Widgets'],
    summary='List Widgets',
    response_model=List[WidgetModel],
)
async def list_widgets(request: Request, db: AsyncSession = Depends(get_db)):
    module = WidgetsModule(request, db)
    return await module.list_widgets()


@router.get(
    '/widgets/{widget_id}',
    tags=['Widgets'],
    summary='Get Widget',
    response_model=WidgetModel,
)
async def get_widget(
    request: Request,
    widget_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_user),
):
    module = WidgetsModule(request, db)
    return await module.get_widget(widget_id)


@router.post(
    '/widgets',
    tags=['Widgets'],
    summary='Create Widget',
    response_model=WidgetModel,
)
async def create_widget(
    request: Request,
    body: WidgetRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_user),
):
    module = WidgetsModule(request, db)
    return await module.create_widget(body)
```

Always pass `request` as the first positional argument when constructing a
module. Always use `Depends(get_db)` — never create a session manually.

### Step 5 — Register the router in `api/main.py`

Open `api/main.py` and add two lines: one import at the top and one
`include_router` call in the app body.

```python
# api/main.py  (after changes)
from api.routers import profile, cats, widgets      # add widgets here
from api.configurations.base import config
from fastapi import FastAPI


class Application(FastAPI):
    def __init__(self, **kwargs):
        config.logger.info("Application starting")
        super().__init__(**kwargs)

app = Application(
    docs_url='/docs',
    swagger_ui_oauth2_redirect_url='/callback',
    title=config.title,
    description="...",
    version="0.0.1",
)

app.include_router(profile.router, prefix=config.prefix)
app.include_router(cats.router, prefix=config.prefix)
app.include_router(widgets.router, prefix=config.prefix)   # add this line
```

All routers are mounted under `config.prefix` (default `/api`). Your routes
will therefore be available at `/api/widgets`, `/api/widgets/{widget_id}`, etc.

### Step 6 — Register the schema in `alembic/env.py`

Open `alembic/env.py` and add an import for the new schema module directly
below the existing schema imports. The import is the side-effect that registers
the ORM model with `Base.metadata` so autogenerate can detect it.

```python
# alembic/env.py  (relevant section)
from api.modules.database import Base
import api.schemas.cats    # noqa: F401
import api.schemas.widgets  # noqa: F401  <-- add this line

from api.configurations.base import config as app_config
config.set_main_option("sqlalchemy.url", app_config.sync_database_url)
target_metadata = Base.metadata
```

Every schema file added to `api/schemas/` must have a corresponding import
here. Without it, autogenerate will not see the new table and will not generate
the migration.

### Step 7 — Commit your feature

After completing all 6 steps above, commit your work:

```bash
git add -A
git commit -m "Feature: Add <feature> CRUD endpoints

- Add <feature> schema in api/schemas/<feature>.py
- Add <feature> models in api/models/<feature>.py
- Add <feature> business logic in api/modules/<feature>.py
- Add <feature> routes in api/routers/<feature>.py
- Register <feature> router in api/main.py
- Register <feature> schema in alembic/env.py
- Add migration in alembic/versions/
- Add e2e tests in tests/e2e/<feature>/test_<feature>.py"
```

Committing after each feature keeps your history clean and enables easy rollback if needed.

---

## Database Configuration

### PostgreSQL (default)

PostgreSQL is the default database. Configuration is read from environment
variables by `api/configurations/base.py`. These variables do NOT use the
`API_` prefix — they bypass `env_prefix` via `validation_alias`:

| Env Var             | Default     | Purpose       |
| ------------------- | ----------- | ------------- |
| `POSTGRES_HOST`     | `localhost` | DB host       |
| `POSTGRES_PORT`     | `5432`      | DB port       |
| `POSTGRES_USERNAME` | `postgres`  | DB user       |
| `POSTGRES_PASSWORD` | _(empty)_   | DB password   |
| `POSTGRES_DB`       | `kittykat`  | Database name |

Two URL properties are derived automatically:

- `config.database_url` — `postgresql+asyncpg://<user>:<pass>@<host>:<port>/<db>`
  Used by the async SQLAlchemy engine in `api/modules/database.py` at runtime.
- `config.sync_database_url` — `postgresql+psycopg2://<user>:<pass>@<host>:<port>/<db>`
  Used exclusively by Alembic in `alembic/env.py` for migrations.

For local development, set overrides in `.env.local` at the project root.
pydantic-settings loads this file automatically:

```
# .env.local
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USERNAME=postgres
POSTGRES_PASSWORD=yourpassword
POSTGRES_DB=kittykat
```

### SQLite (local dev alternative)

SQLite requires no running server and is useful for lightweight local
development. To use it:

1. Add the `aiosqlite` async driver:

   ```bash
   uv add aiosqlite
   ```

2. Override the database URL properties. The URL formats are:
   - Runtime (async): `sqlite+aiosqlite:///./app.db`
   - Alembic (sync): `sqlite:///./app.db`

3. Modify `api/modules/database.py` to use the SQLite URL:

   ```python
   engine = create_async_engine("sqlite+aiosqlite:///./app.db", echo=config.debug)
   ```

4. Modify `alembic/env.py` to use the sync SQLite URL:

   ```python
   config.set_main_option("sqlalchemy.url", "sqlite:///./app.db")
   ```

5. Run migrations as usual:
   ```bash
   alembic upgrade head
   ```

### Switching between PostgreSQL and SQLite

To switch between databases without editing code, add an `API_DB_BACKEND`
environment variable to `api/configurations/base.py`:

```python
class Settings(BaseSettings):
    # ...
    db_backend: str = Field('postgresql', validation_alias='API_DB_BACKEND')

    @property
    def database_url(self) -> str:
        if self.db_backend == 'sqlite':
            return "sqlite+aiosqlite:///./app.db"
        return f"postgresql+asyncpg://{self.postgres_username}:..."

    @property
    def sync_database_url(self) -> str:
        if self.db_backend == 'sqlite':
            return "sqlite:///./app.db"
        return f"postgresql+psycopg2://{self.postgres_username}:..."
```

Then set `API_DB_BACKEND=sqlite` in `.env.local` to use SQLite locally.

---

## Alembic Migrations

Alembic manages all schema changes. Never create or modify tables by hand.

### Workflow: add a table or column

```bash
# 1. Ensure your schema file exists and is imported in alembic/env.py
# 2. Generate the migration (compares ORM models to the live DB)
alembic revision --autogenerate -m "add widgets table"

# 3. Review the generated file in alembic/versions/
#    Confirm upgrade() creates the right columns and downgrade() drops them.

# 4. Apply it
alembic upgrade head
```

### Common commands

```bash
alembic upgrade head        # apply all pending migrations
alembic downgrade -1        # revert the most recent migration
alembic downgrade base      # revert all migrations (empty DB)
alembic current             # show current revision
alembic history             # list all revisions
alembic history -r current:head   # show pending (not yet applied)
alembic heads               # show latest revision(s)
alembic stamp head          # mark DB as at head without running SQL
```

### What `alembic/env.py` must contain

`alembic/env.py` has three responsibilities. Do not remove any of them:

1. Import `Base` from `api.modules.database` — this provides `target_metadata`.
2. Import every schema module under `api/schemas/` — these imports register ORM
   models as a side effect. Without them, autogenerate will generate drop-table
   statements for existing tables.
3. Override `sqlalchemy.url` using `app_config.sync_database_url` — the value
   in `alembic.ini` is a fallback only and should not be relied upon.

```python
from api.modules.database import Base
import api.schemas.cats    # noqa: F401
import api.schemas.widgets  # noqa: F401   <- add for every new schema file

from api.configurations.base import config as app_config
config.set_main_option("sqlalchemy.url", app_config.sync_database_url)
target_metadata = Base.metadata
```

### Migration file naming

Alembic generates files in `alembic/versions/` using a random hex revision ID.
If you prefer human-readable IDs (e.g. `0002_add_widgets_table.py`), rename
the file and update the `revision` variable inside it to match. The existing
migration `0001_initial_cats_schema.py` uses this pattern.

---

## Error Handling

### Raising errors in modules

Use `APIError` from `api.exceptions.api`. Pass a key from `ErrorMessages.ERRORS`
plus any required keyword arguments:

```python
from api.exceptions.api import APIError

# 404 — resource not found
raise APIError("not_found", field="widget_id", value=widget_id)

# 400 — general business logic error with custom message
raise APIError("general_error", text="Widget is out of stock")

# 400 — duplicate resource
raise APIError("duplicated_resource", value="widget")

# 400 — invalid field value
raise APIError("invalid_field_value", field="quantity", value=body.quantity)

# 403 — forbidden action
raise APIError("authorization_error", text="You do not own this widget")
```

The `APIError` constructor calls `ErrorMessages(key, **params)`, formats the
message string using `%` interpolation, and delegates to `HTTPException` with
the correct status code. No other exception class should be used for business
errors.

### Adding a new error key

Open `api/exceptions/api.py` and add a new entry to `ErrorMessages.ERRORS`.
Each entry is a 3-tuple: `(status_code, reason_phrase, message_template)`.
Message templates use `%(param_name)s` placeholders.

```python
# api/exceptions/api.py  — inside ErrorMessages.ERRORS
'widget_unavailable': (
    409,
    'Widget unavailable',
    'Widget "%(name)s" is currently unavailable',
),
```

Then raise it with:

```python
raise APIError("widget_unavailable", name=widget.name)
```

Do not add new exception classes. All errors flow through `APIError`.

---

## Authentication

### How `require_user` works

`require_user` is a FastAPI dependency defined in `api/models/auth.py`. It:

1. Extracts the `Authorization: Bearer <token>` header via `HTTPBearer`.
2. Decodes the JWT using `config.signature_text` (env: `API_SIGNATURE_TEXT`,
   default `"somesecret"`) and algorithm `HS256`.
3. Returns the decoded payload as a `UserModel` (fields: `id`, `name`, `sub`,
   `iat`, `exp`).
4. Raises `APIError("unauthorized")` (HTTP 401) on missing, expired, or
   malformed tokens.

### When to use it

Add `user=Depends(require_user)` to any route that requires authentication.
Pass the `user` object to the module method when user identity is needed in
business logic.

```python
# Router — authenticated endpoint
@router.delete('/widgets/{widget_id}', response_model=WidgetModel)
async def delete_widget(
    request: Request,
    widget_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_user),
):
    module = WidgetsModule(request, db)
    return await module.delete_widget(widget_id, user)
```

```python
# Module — using user identity
async def delete_widget(self, widget_id: str, user):
    widget = await self.get_widget(widget_id)
    if widget.owner_id != user["id"]:
        raise APIError("authorization_error", text="You do not own this widget")
    await self.db.delete(widget)
    await self.db.commit()
    return widget
```

Omit `require_user` for public routes (e.g. `GET /cats`, `GET /health`).

---

## Testing

### Infrastructure

Tests are e2e using FastAPI's synchronous `TestClient`. There is no mocking of
the database layer — tests run against the actual app with its real dependency
injection. Fixtures are registered globally in `conftest.py` at the project
root:

```python
# conftest.py
pytest_plugins = [
    'tests.e2e.conf._conftest_auth',
    'tests.e2e.conf._conftest_common',
]
```

Available fixtures (no import needed in test files — pytest discovers them):

| Fixture           | Scope    | Provides                                                        |
| ----------------- | -------- | --------------------------------------------------------------- |
| `function_client` | function | `CustomClient` wrapping the app, no auth                        |
| `mock_user_token` | function | Pre-built HS256 JWT signed with `"somesecret"`                  |
| `mock_user`       | function | `MockUser(access_token)` instance                               |
| `user_client`     | function | `CustomClient` with `mock_user` set; auto-injects Bearer header |

### CustomClient and MockUser

`CustomClient` (in `tests/e2e/__init__.py`) extends `TestClient`. It overrides
`request()` to inject `Authorization: Bearer <token>` on every call, reading
from `self.user.access_token`. Use `user_client` when testing authenticated
endpoints; use `function_client` when testing public endpoints.

`MockUser` is a minimal object with a single `access_token` attribute. The
pre-built test token in `_conftest_auth.py` is signed with `"somesecret"` and
contains `{"sub": "1234567890", "name": "some_name", "id": "someid"}`.

### Writing a test file

Create `tests/e2e/<feature>/test_<feature>.py`. Mark the file with a pytest
marker matching the feature name. Register the marker in `pytest.ini`.

```python
# tests/e2e/widgets/test_widgets.py
import pytest

pytestmark = pytest.mark.widgets


def test_list_widgets_public(function_client):
    response = function_client.get("/api/widgets")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_widget_not_found(user_client):
    response = user_client.get("/api/widgets/nonexistent-id")
    assert response.status_code == 404


def test_create_widget_requires_auth(function_client):
    response = function_client.post("/api/widgets", json={
        "name": "Test Widget",
        "description": "A widget for testing",
        "quantity": 5,
    })
    assert response.status_code == 403


def test_create_widget(user_client):
    response = user_client.post("/api/widgets", json={
        "name": "Test Widget",
        "description": "A widget for testing",
        "quantity": 5,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Widget"
    assert "id" in data
```

Register the marker in `pytest.ini`:

```ini
[pytest]
markers =
    profile
    widgets     # add one line per new feature
```

### Running tests

```bash
pytest                                      # all tests
pytest tests/e2e/widgets/                  # feature-specific
pytest -m widgets                          # by marker
pytest tests/e2e/widgets/test_widgets.py   # single file
```

---

## User Requirements

Fill in this section before starting implementation. The agent will use this
information to determine resource names, fields, authentication requirements,
and any business rules.

```
Feature name:
  (e.g. "widgets", "bookings", "reviews")

Resource description:
  (What does this resource represent?)

Database table name:
  (snake_case plural, e.g. "widgets")

Fields (name, type, nullable, default):
  -
  -
  -

Relationships (ForeignKey to which table):
  -

Endpoints needed:
  [ ] GET    /<resource>          (list all)
  [ ] GET    /<resource>/{id}     (get one)
  [ ] POST   /<resource>          (create)
  [ ] PUT    /<resource>/{id}     (update)
  [ ] DELETE /<resource>/{id}     (delete)

Authentication:
  Which endpoints require require_user?
  -

Business rules / validation:
  -

Error cases to handle:
  -

Test cases to cover:
  -

Additional notes:
  -
```

Build a doll shop backend apis including crud operations for common features, like listing/filtering dolls based on price, category, material, size, weight etc.

order placemement, purchase history of the user, user filtering (include common user/customer details).
