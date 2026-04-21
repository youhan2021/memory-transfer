#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from apply_import import apply_import
from export_memory import load_source_bundle


def load_bundle(path: Path) -> dict:
    if path.suffix.lower() == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict) and "memories" in payload:
            return payload
    return load_source_bundle(path)


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9._-]+", "-", value).strip("-_.").lower()
    return slug or "memory"


def directory_mode_requested(path: Path, raw_target: str) -> bool:
    return (path.exists() and path.is_dir()) or raw_target.endswith("/") or path.suffix == ""


def load_target(path: Path) -> list[dict]:
    if not path.exists():
        return []
    if path.is_dir():
        return load_source_bundle(path).get("memories", [])
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        return payload.get("memories", [])
    return payload


def render_memory_markdown(memory: dict) -> str:
    metadata = {
        "id": memory["id"],
        "type": memory["type"],
        "title": memory["title"],
        "tags": memory.get("tags", []),
        "transferable": memory.get("transferable", True),
        "sensitivity": memory.get("sensitivity", "low"),
    }
    return (
        f"# {memory['title']}\n\n"
        f"{memory['content'].rstrip()}\n\n"
        f"<!-- memory-transfer-meta: {json.dumps(metadata, ensure_ascii=False)} -->\n"
    )


def write_directory_target(path: Path, memories: list[dict], mode: str) -> None:
    path.mkdir(parents=True, exist_ok=True)

    if mode == "replace":
        for existing_file in path.iterdir():
            if existing_file.is_file() and existing_file.suffix.lower() in {".md", ".txt"}:
                existing_file.unlink()

    for memory in memories:
        filename = f"{slugify(memory['id'])}.md"
        (path / filename).write_text(render_memory_markdown(memory), encoding="utf-8")


def write_file_target(path: Path, memories: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"memories": memories}, indent=2) + "\n", encoding="utf-8")


def import_bundle_to_target(bundle: dict, raw_target: str, mode: str) -> dict[str, object]:
    target_path = Path(raw_target).expanduser().resolve()
    incoming = bundle.get("memories", [])
    existing = load_target(target_path)
    merged = apply_import(existing, incoming, mode)

    target_is_directory = directory_mode_requested(target_path, raw_target)
    if target_is_directory:
        write_directory_target(target_path, merged, mode)
    else:
        write_file_target(target_path, merged)

    return {
        "target": str(target_path),
        "target_mode": "directory" if target_is_directory else "json_file",
        "mode": mode,
        "existing_count": len(existing),
        "incoming_count": len(incoming),
        "result_count": len(merged),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Import a memory bundle into a local target file.")
    parser.add_argument("--bundle", required=True, help="Path to bundle JSON")
    parser.add_argument(
        "--target",
        required=True,
        help="Path to target JSON file or target directory for markdown memory files",
    )
    parser.add_argument(
        "--mode",
        default="upsert",
        choices=["append", "replace", "upsert"],
        help="Import mode",
    )
    args = parser.parse_args()

    bundle_path = Path(args.bundle).expanduser().resolve()
    bundle = load_bundle(bundle_path)
    summary = import_bundle_to_target(bundle, args.target, args.mode)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
