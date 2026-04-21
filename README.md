# memory-transfer

`memory-transfer` is a low-friction MVP for selective agent memory export and import. It is intentionally not an account system, not a sync engine, and not a long-term cloud storage product. The goal is a minimal `export -> preview -> import -> consume` loop that works well with QR payloads, short codes, and a temporary relay backend.

## Project Goal

This repo contains:

- A Python + FastAPI backend for temporary bundle relay
- An OpenClaw-style skill package focused on memory transfer
- Shared schemas, examples, and protocol docs
- A repo-level install flow for contributors
- A standalone skill install flow for end users

## Install Modes

There are now two different install paths:

- `skill-only install`: for users who only need the OpenClaw skill
- `repo/dev install`: for contributors who want the backend, docs, tests, and skill together

### Skill-Only Install

The skill is intended to be installable on its own, without cloning the full monorepo.

Recommended remote install command:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/youhan2021/memory-transfer/main/install-skill.sh)
```

The installer will ask for `MEMORY_TRANSFER_SERVER_URL` and write it into the installed skill's `config.env`.
It will also ask for the target skill install directory, so Hermes/OpenClaw users can choose the correct runtime skills path.
You can also preseed it:

```bash
MEMORY_TRANSFER_SERVER_URL=http://127.0.0.1:8000/ bash <(curl -fsSL https://raw.githubusercontent.com/youhan2021/memory-transfer/main/install-skill.sh)
```

Or preseed both values:

```bash
MEMORY_TRANSFER_SKILLS_DIR=~/.hermes/skills MEMORY_TRANSFER_SERVER_URL=http://127.0.0.1:8000/ bash <(curl -fsSL https://raw.githubusercontent.com/youhan2021/memory-transfer/main/install-skill.sh)
```

If you already cloned this repo locally, run:

```bash
./install-skill.sh
```

Supported skill install modes:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/youhan2021/memory-transfer/main/install-skill.sh)
bash <(curl -fsSL https://raw.githubusercontent.com/youhan2021/memory-transfer/main/install-skill.sh) --copy
./install-skill.sh --link
./install-skill.sh --copy
```

That installer only does one thing:

- install the `memory-transfer` skill into your local OpenClaw skills directory

Default target:

```text
~/.openclaw/skills/memory-transfer
```

### Repo / Dev Install

Use the repo-level installer only when you want the backend and local development environment too:

```bash
cd ~/memory-transfer
./install.sh
```

The repo installer will:

- check for `python3`
- ensure `uv` is available
- sync backend dependencies with `uv`
- create runtime directories
- install the `memory-transfer` skill into your local OpenClaw skills directory

Supported repo install modes:

```bash
./install.sh
./install.sh --link
./install.sh --copy
./install.sh --dev
```

## Backend

Start the backend with:

```bash
make dev-backend
```

Or directly:

```bash
cd backend
uv sync --group dev
uv run uvicorn memory_transfer_server.main:app --app-dir src --reload --host 0.0.0.0 --port 8000
```

Available MVP endpoints:

- `GET /health`
- `POST /transfer/create`
- `GET /transfer/{transfer_id}`
- `POST /transfer/{transfer_id}/consume`

## Skill Install Location

Both installers resolve the skill destination in this order:

- `$OPENC LAW_SKILLS_DIR` when set exactly as that environment variable name
- otherwise `$OPENCLAW_SKILLS_DIR` when set
- otherwise `~/.openclaw/skills`

Default installed path:

```text
~/.openclaw/skills/memory-transfer
```

## Basic Flow

1. Export memories from a source file with `skills/memory-transfer/scripts/export_memory.py`
2. Create a bundle and send it to the backend with `POST /transfer/create`
3. Share the returned `transfer_id`, short code, or QR payload
4. Preview from the target side before importing
5. Import with `append`, `replace`, or `upsert`
6. Optionally call consume for one-time transfer semantics

## Uninstall Or Reinstall

Remove the installed skill directory:

```bash
rm -rf ~/.openclaw/skills/memory-transfer
```

Reinstall the skill only:

```bash
./install-skill.sh --link
```

Reinstall the whole repo dev setup:

```bash
./install.sh --link
```

If you want a clean backend environment:

```bash
rm -rf backend/.venv backend/.data
./install.sh
```
