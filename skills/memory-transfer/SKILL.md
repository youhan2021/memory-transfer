# memory-transfer

## Purpose

This skill helps move stable, exportable memories from one agent context to another. It is explicitly about selective transfer, not real-time synchronization.

## What It Does

- exports transferable memories from a local file-based source
- uploads a bundle to the configured relay backend
- previews a bundle before import
- generates QR-friendly payload text
- imports a bundle into a local target store with `append`, `replace`, or `upsert`
- reads backend server settings from `config.env` inside the skill directory

## Workflow

1. Export from a source bundle or directly from local memory files with `scripts/export_memory.py`
2. Ask the user whether they want `二维码` / `短码` / `两者都要`
3. Upload the bundle with `scripts/create_transfer.py`
4. Return the requested transfer result directly after upload, including a ready-to-send import prompt
5. Optionally preview with `scripts/preview_bundle.py`
6. Import with `scripts/import_memory.py`

## Rules

- Prefer stable memory types such as `preference`, `profile`, `project_context`, `workflow`, and `tool_preference`
- Exclude `temporary` items by default
- Exclude local path, device-specific, and cache-like items by default
- Use preview before applying import when possible
- If there is no existing bundle, do not ask the user to prepare one first; generate a minimal bundle directly from available `.md` or `.txt` memory files
- When a single local memory note is available, treat it as source material and package it into a bundle automatically
- When the user wants to transfer, do not stop after local export; ask which transfer output they want, upload to the server, and return the corresponding code immediately
- After upload, always show the import prompt, especially the short-code based import prompt
- If the user does not specify a preference, default to returning both `short_code` and `qr_payload`

## Files

- `openclaw.yaml`: OpenClaw-facing metadata
- repo-root `install-skill.sh`: standalone skill install entrypoint
- `config.env`: local server config, ignored by git
- `config.env.example.txt`: example server config template
- `references/`: bundle and import behavior references
- `scripts/`: runnable helpers
- `tests/`: basic script tests
