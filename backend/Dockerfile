FROM python:3.14-slim

# Copy the AWS Lambda Web Adapter binary into the extensions directory
COPY --from=public.ecr.aws/awsguru/aws-lambda-adapter:1.0.1 /lambda-adapter /opt/extensions/lambda-adapter

# Install the uv binary for package management. See: https://docs.astral.sh/uv/guides/integration/docker/#installing-uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV PATH="/bin:${PATH}"
ENV UV_CACHE_DIR="/root/.cache/uv"

# Copy from the cache instead of linking
ENV UV_LINK_MODE=copy

# Have uv compile packages to .pyc Python bytecode at installation time, improving
# application runtime performance
ENV UV_COMPILE_BYTECODE=1

# Omit development dependencies
ENV UV_NO_DEV=1

# Ensure installed tools can be executed out of the box
ENV UV_TOOL_BIN_DIR=/usr/local/bin

WORKDIR /app

# Install dependencies
COPY pyproject.toml .
COPY uv.lock .
RUN uv sync

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Copy backend application code
COPY main.py .

# Expose the internal port the web server will run on
EXPOSE 8080
ENV PORT=8080

# Run the application using uvicorn with the AWS Lambda Web Adapter
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]