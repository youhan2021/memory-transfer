# memory-transfer

## Purpose

This skill helps move stable, exportable memories from one agent context to another. It is explicitly about selective transfer, not real-time synchronization.

## What It Does

- exports transferable memories from a local file-based source
- uploads a bundle to the configured relay backend
- looks up a preview by short code
- confirms import with short code plus confirm phrase
- imports a bundle into a local target store with `append`, `replace`, or `upsert`
- reads backend server settings from `config.env` inside the skill directory

## Workflow

1. Export from a source bundle or directly from local memory files with `scripts/export_memory.py`
2. Upload the bundle with `scripts/create_transfer.py`
3. Show the user `short_code`, `confirm_phrase`, and expiry
4. On the target side, run lookup with `scripts/lookup_transfer.py`
5. Ask the user for the confirm phrase after preview
6. Confirm and import with `scripts/confirm_import.py`

## Rules

- Do not apply automatic export filtering rules by default
- Export should keep memories as-is unless the user explicitly asks for type filtering
- Use preview before applying import when possible
- If there is no existing bundle, do not ask the user to prepare one first; generate a minimal bundle directly from available `.md` or `.txt` memory files
- When a single local memory note is available, treat it as source material and package it into a bundle automatically
- The only pairing method is `short_code` plus `confirm_phrase`
- Do not mention alternative pairing methods, scan flows, links, or login
- After source export, show `short_code`, `confirm_phrase`, and expiry
- On the target side, do not import immediately after short code lookup; preview first and require confirm phrase
- The import prompt should be rule-based and template-generated, not free-written
- Do not output shell commands, Python commands, local paths, or CLI snippets when returning the next-step transfer instruction
- Use a fixed sentence template such as: `请用 memory-transfer skill lookup 这份记忆。短码是 XXXX。拿到 preview 后，再让我输入 confirm phrase。`
- `scripts/create_transfer.py` should default to prompt-style text output, not JSON, so callers naturally surface the prompt instead of inventing CLI

## Response Format

When export + upload succeeds, the response must follow this structure:

```text
导出成功：
Short Code: XXXX
Confirm phrase: silver bamboo
Expires at: 2026-04-21T01:00:00Z
发给目标机器 agent：
请用 memory-transfer skill lookup 这份记忆。短码是 XXXX。拿到 preview 后，再让我输入 confirm phrase。
```

## Forbidden Output

After a transfer is created, do not output any of the following:

- `python ...`
- `python3 ...`
- `bash ...`
- `curl ...`
- filesystem paths such as `~/.openclaw/...` or `/tmp/bundle.json`
- multi-step CLI import instructions
- alternate pairing mechanisms
- scan-oriented workflows

Bad example:

```text
目标机器导入：
python3 ... lookup_transfer.py ...
python3 ... confirm_import.py ...
```

This output is not allowed. Replace it with the fixed prompt format above.

## Files

- `openclaw.yaml`: OpenClaw-facing metadata
- repo-root `install-skill.sh`: standalone skill install entrypoint
- `config.env`: local server config, ignored by git
- `config.env.example.txt`: example server config template
- `references/`: bundle and import behavior references
- `scripts/`: runnable helpers
