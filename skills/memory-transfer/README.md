# memory-transfer skill

This skill is designed for local, file-based demonstrations of agent memory transfer.

It should be installable on its own. Users should not need to clone the full monorepo just to install the skill.

The primary installer entrypoint lives at the repository root as `install-skill.sh`, so remote install can use a simple GitHub raw URL.

## Standalone Install

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/youhan2021/memory-transfer/main/install-skill.sh)
```

Supported modes:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/youhan2021/memory-transfer/main/install-skill.sh)
bash <(curl -fsSL https://raw.githubusercontent.com/youhan2021/memory-transfer/main/install-skill.sh) --copy
./install-skill.sh --link
./install-skill.sh --copy
```

## Scripts

- `export_memory.py`: export a filtered bundle
- `preview_bundle.py`: summarize a bundle before import
- `generate_qr.py`: produce transfer payload text and optional ASCII QR placeholder output
- `import_memory.py`: import into a local target file
- `apply_import.py`: import mode implementation helper
- `install_local.sh`: local helper used by the repo-level skill installer

## Repo-Local Install

```bash
bash scripts/install_local.sh --link
```

## Example

```bash
python scripts/export_memory.py --source ../../examples/sample-memory-bundle.json
python scripts/preview_bundle.py --bundle ../../examples/sample-memory-bundle.json
python scripts/import_memory.py --bundle ../../examples/sample-memory-bundle.json --target ../../dist/imported-memories.json --mode upsert
```
