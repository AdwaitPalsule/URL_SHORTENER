
FROM python:3.11-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set the application directory
WORKDIR /app

# Configure Python and uv
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_PROJECT_ENVIRONMENT=/app/.venv

# Copy dependency files first for better build caching
COPY pyproject.toml uv.lock ./

# Install locked production dependencies only
ENV UV_HTTP_TIMEOUT=120
ENV UV_HTTP_RETRIES=10
RUN uv sync --frozen --no-dev --no-install-project

# Copy application code and migrations
COPY . .

# Start the FastAPI server
EXPOSE 8000

CMD ["/app/.venv/bin/uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

