# Validation Progress

## Issues Found and Fixed

1.  **Auth Commented Out in Routers**: 
    - Found that all `user=Depends(require_user)` were commented out in `api/routers/`.
    - **Fix**: Uncommented all auth dependencies to ensure the API is actually secured.

2.  **TypeError in Test Client**: 
    - Found a bug in `tests/e2e/__init__.py` where `headers = kwargs.get("headers", {})` failed if `headers` was explicitly passed as `None`.
    - **Fix**: Changed to `headers = kwargs.get("headers") or {}`.

3.  **JWT ImmatureSignatureError**: 
    - Found that `tests/e2e/conf/_conftest_auth.py` used `datetime.utcnow().timestamp()`, which produces a shifted timestamp on systems where local time is not UTC.
    - **Fix**: Switched to `datetime.now(timezone.utc).timestamp()`.

4.  **Missing Fields in Test Requests**: 
    - Many tests were sending incomplete data (missing `type`, `weight`, `phone`), leading to `422 Unprocessable Entity` errors.
    - **Fix**: Updated all E2E tests to include required fields.

5.  **Event Loop Mismatch (TestClient + asyncpg)**: 
    - FastAPI's sync `TestClient` runs the app in a separate thread, causing `asyncpg` to fail with `RuntimeError` due to different event loops.
    - **Workaround/Fix**: Modified `api/modules/database.py` to create a new engine/session per request during validation. *Note: For production, switching to AsyncClient is recommended.*

6.  **Lazy Loading during Response Serialization**: 
    - Order creation failed because `items` were lazy-loaded during serialization outside of the async session context.
    - **Fix**: Updated `OrdersModule.create_order` to eagerly load the order with items before returning.

7.  **Duplicate Email Errors in Tests**: 
    - Tests failed on subsequent runs due to unique email constraints.
    - **Fix**: Updated tests to use unique emails per run.

## Final Status
All 12 E2E tests are now PASSING.
The application starts up and responds to requests correctly.
