# Use a Python base image
FROM ghcr.io/astral-sh/uv:python3.10-bookworm-slim

# Set the working directory
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a container
ENV UV_LINK_MODE=copy

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Copy the application code
COPY . .

# Expose the port
EXPOSE 9999

# Make entrypoint script executable
RUN chmod +x entrypoint.sh

# Command to run the application
ENTRYPOINT ["./entrypoint.sh"]
