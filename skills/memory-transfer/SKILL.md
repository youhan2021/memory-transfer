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
- The import prompt should be rule-based and template-generated, not free-written
- Do not output shell commands, Python commands, local paths, or CLI snippets when returning the next-step transfer instruction
- Use a fixed sentence template such as: `请用 memory-transfer skill 从服务器拉取并导入这份记忆。短码是 XXXX。先 preview，再用 upsert 模式导入。`
- `scripts/create_transfer.py` should default to prompt-style text output, not JSON, so callers naturally surface the prompt instead of inventing CLI

## Response Format

When export + upload succeeds, the response must follow this structure:

```text
导出成功：
Short Code: XXXX
Transfer ID: YYYY
发给目标机器 agent：
请用 memory-transfer skill 从服务器拉取并导入这份记忆。短码是 XXXX。先 preview，再用 upsert 模式导入。
```

If the user asked for QR code only, replace the last line with:

```text
请用 memory-transfer skill 从服务器拉取并导入这份记忆。二维码 payload 是 ZZZZ。先 preview，再用 upsert 模式导入。
```

If both are requested, prefer the short-code prompt in the main response and optionally include the QR payload on a separate line.

## Forbidden Output

After a transfer is created, do not output any of the following:

- `python ...`
- `python3 ...`
- `bash ...`
- `curl ...`
- filesystem paths such as `~/.openclaw/...` or `/tmp/bundle.json`
- multi-step CLI import instructions

Bad example:

```text
目标机器导入：
python3 ~/.openclaw/skills/memory-transfer/scripts/fetch_transfer.py --short-code XXXX --output /tmp/bundle.json
python3 ~/.openclaw/skills/memory-transfer/scripts/import_memory.py --bundle /tmp/bundle.json --target ~/.hermes/memories/ --mode upsert
```

This output is not allowed. Replace it with the fixed prompt format above.

## Files

- `openclaw.yaml`: OpenClaw-facing metadata
- repo-root `install-skill.sh`: standalone skill install entrypoint
- `config.env`: local server config, ignored by git
- `config.env.example.txt`: example server config template
- `references/`: bundle and import behavior references
- `scripts/`: runnable helpers
- `tests/`: basic script tests
