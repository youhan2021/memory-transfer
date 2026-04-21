#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is required but was not found. Run ../install.sh first." >&2
  exit 1
fi

uv sync --group dev
exec uv run uvicorn memory_transfer_server.main:app --app-dir src --reload --host 0.0.0.0 --port 8000
