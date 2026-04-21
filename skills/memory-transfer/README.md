# memory-transfer skill

This skill is designed for local, file-based demonstrations of agent memory transfer.

It should be installable on its own. Users should not need to clone the full monorepo just to install the skill.

The primary installer entrypoint lives at the repository root as `install-skill.sh`, so remote install can use a simple GitHub raw URL.

## Server Config

The skill reads backend server config from:

- `config.env`: local, ignored by git
- `config.env.example.txt`: committed example

Example value:

```text
MEMORY_TRANSFER_SERVER_URL=http://127.0.0.1:8000/
```

## Standalone Install

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/youhan2021/memory-transfer/main/install-skill.sh)
```

During install, the script will ask for `MEMORY_TRANSFER_SERVER_URL` and save it to `config.env`.
You can also pass it non-interactively:

```bash
MEMORY_TRANSFER_SERVER_URL=http://127.0.0.1:8000/ bash <(curl -fsSL https://raw.githubusercontent.com/youhan2021/memory-transfer/main/install-skill.sh)
```

Supported modes:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/youhan2021/memory-transfer/main/install-skill.sh)
bash <(curl -fsSL https://raw.githubusercontent.com/youhan2021/memory-transfer/main/install-skill.sh) --copy
./install-skill.sh --link
./install-skill.sh --copy
```

## Scripts

- `export_memory.py`: export a filtered bundle, or auto-build one from `.md` / `.txt` memory files
- `create_transfer.py`: upload a bundle to the configured backend and return `short_code`, `qr_payload`, or both, plus agent-facing import prompts
- `fetch_transfer.py`: fetch a bundle from the backend by `transfer_id` or `short_code`
- `preview_bundle.py`: summarize a bundle before import
- `generate_qr.py`: produce transfer payload text and optional ASCII QR placeholder output
- `import_memory.py`: import into a local target file
- `apply_import.py`: import mode implementation helper
- `skill_config.py`: reads `config.env` and returns the configured backend server URL
- `install_local.sh`: local helper used by the repo-level skill installer

## Repo-Local Install

```bash
bash scripts/install_local.sh --link
```

## Example

```bash
python scripts/export_memory.py --source ../../examples/sample-memory-bundle.json
python scripts/export_memory.py --source ../../memory
python scripts/export_memory.py --source ../../memory/2026-04-18-moyu-threebody.md
python scripts/create_transfer.py --source ../../memory --output-kind both
python scripts/create_transfer.py --source ../../memory/2026-04-18-moyu-threebody.md --output-kind qr
python scripts/fetch_transfer.py --short-code ABC123 --output ./dist/fetched-ABC123.json
python scripts/preview_bundle.py --bundle ../../examples/sample-memory-bundle.json
python scripts/import_memory.py --bundle ../../examples/sample-memory-bundle.json --target ../../dist/imported-memories.json --mode upsert
```
