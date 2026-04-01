# Claude Status

The repository is now fully functional and validated.

## Key Fixes

- Secured all authenticated endpoints by uncommenting `require_user` dependencies.
- Fixed critical bugs in the E2E test suite (JWT timestamps, Header handling, Missing fields).
- Resolved `RuntimeError` and `InterfaceError` caused by asyncpg/event-loop mismatch in tests.
- Fixed `ResponseValidationError` in orders due to lazy loading.

## How to Run Tests

```bash
uv sync
uv run pytest
```

## How to Start the App

```bash
uv run python run.py
```

The API is available at `http://localhost:9999/api`.
Interactive docs at `http://localhost:9999/docs`.
