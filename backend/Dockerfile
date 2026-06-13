FROM python:3.13-slim

# Install uv from the official image (fast, standalone — no pip involved).
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN useradd -m appuser

WORKDIR /app
RUN chown appuser:appuser /app

USER appuser

# Compile bytecode for faster cold starts; copy (not hardlink) for volume safety.
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Install locked dependencies first for better layer caching.
# uv sync uses uv.lock for fully reproducible, exact versions (no pip).
COPY --chown=appuser:appuser pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

# Put the synced venv on PATH so uvicorn resolves without `uv run`.
ENV PATH="/app/.venv/bin:$PATH"

COPY --chown=appuser:appuser . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
