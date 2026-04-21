# Backend

This FastAPI service provides a temporary relay for memory bundles.

## Features

- in-memory store with optional local JSON snapshot persistence
- TTL expiration
- short code plus confirm phrase pairing
- preview lookup without exposing full memory content
- one-time confirm-import consumption

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
