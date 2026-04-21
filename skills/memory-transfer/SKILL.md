# memory-transfer

## Purpose

This skill helps move stable, exportable memories from one agent context to another. It is explicitly about selective transfer, not real-time synchronization.

## What It Does

- exports transferable memories from a local file-based source
- previews a bundle before import
- generates QR-friendly payload text
- imports a bundle into a local target store with `append`, `replace`, or `upsert`

## Workflow

1. Export from a source file with `scripts/export_memory.py`
2. Optionally preview with `scripts/preview_bundle.py`
3. Optionally generate a QR payload with `scripts/generate_qr.py`
4. Import with `scripts/import_memory.py`

## Rules

- Prefer stable memory types such as `preference`, `profile`, `project_context`, `workflow`, and `tool_preference`
- Exclude `temporary` items by default
- Exclude local path, device-specific, and cache-like items by default
- Use preview before applying import when possible

## Files

- `openclaw.yaml`: OpenClaw-facing metadata
- repo-root `install-skill.sh`: standalone skill install entrypoint
- `references/`: bundle and import behavior references
- `scripts/`: runnable helpers
- `tests/`: basic script tests
