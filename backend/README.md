# Backend

This FastAPI service provides a temporary relay for memory bundles.

## Features

- in-memory store with optional local JSON snapshot persistence
- TTL expiration
- preview fetch
- one-time consume support

## Development

```bash
cd backend
uv sync --group dev
uv run uvicorn memory_transfer_server.main:app --app-dir src --reload
```

## Tests

```bash
cd backend
uv run pytest
```
