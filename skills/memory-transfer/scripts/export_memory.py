#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_EXPORT_TYPES = {
    "preference",
    "profile",
    "project_context",
    "workflow",
    "tool_preference",
}
DEFAULT_EXCLUDED_TYPES = {"temporary"}
TEXT_EXTENSIONS = {".md", ".txt"}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def guess_memory_type(path: Path, content: str) -> str:
    lowered = f"{path.name} {content}".lower()
    if any(token in lowered for token in ("workflow", "process", "routine")):
        return "workflow"
    if any(token in lowered for token in ("profile", "bio", "identity")):
        return "profile"
    if any(token in lowered for token in ("tool", "editor", "cli", "terminal")):
        return "tool_preference"
    if any(token in lowered for token in ("prefer", "preference", "喜欢", "偏好")):
        return "preference"
    return "project_context"


def make_memory_id(path: Path, content: str) -> str:
    digest = hashlib.sha1(f"{path}:{content}".encode("utf-8")).hexdigest()[:12]
    return f"mem_{digest}"


def memory_from_text_file(path: Path) -> dict:
    content = path.read_text(encoding="utf-8").strip()
    if not content:
        return {
            "id": make_memory_id(path, ""),
            "type": "temporary",
            "title": path.stem,
            "content": "",
            "tags": [path.suffix.lstrip(".")] if path.suffix else [],
            "transferable": False,
            "sensitivity": "low",
        }

    inferred_type = guess_memory_type(path, content)
    lowered = content.lower()
    transferable = not any(
        token in lowered for token in ("cache", "/tmp", "device id", "localhost-only")
    )
    return {
        "id": make_memory_id(path, content),
        "type": inferred_type,
        "title": path.stem.replace("-", " ").replace("_", " ").strip() or path.name,
        "content": content,
        "tags": [path.suffix.lstrip(".")] if path.suffix else [],
        "transferable": transferable and inferred_type not in DEFAULT_EXCLUDED_TYPES,
        "sensitivity": "medium" if any(token in lowered for token in ("private", "sensitive")) else "low",
    }


def bundle_from_memory_files(source_path: Path) -> dict:
    if source_path.is_dir():
        candidates = sorted(
            path for path in source_path.rglob("*") if path.is_file() and path.suffix.lower() in TEXT_EXTENSIONS
        )
    else:
        candidates = [source_path]

    memories = [
        memory_from_text_file(path)
        for path in candidates
        if path.suffix.lower() in TEXT_EXTENSIONS
    ]
    return {
        "version": "1.0",
        "source_agent": source_path.stem if source_path.is_file() else source_path.name or "local-memory-source",
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "memories": memories,
    }


def load_source_bundle(path: Path) -> dict:
    if path.suffix.lower() == ".json":
        payload = load_json(path)
        if isinstance(payload, dict) and "memories" in payload:
            return payload
    return bundle_from_memory_files(path)


def filter_memories(bundle: dict, include_types: set[str] | None = None) -> dict:
    include_types = include_types or DEFAULT_EXPORT_TYPES
    filtered = []
    for memory in bundle.get("memories", []):
        memory_type = memory.get("type")
        content = str(memory.get("content", "")).lower()
        if not memory.get("transferable", False):
            continue
        if memory_type in DEFAULT_EXCLUDED_TYPES:
            continue
        if memory_type not in include_types:
            continue
        if any(token in content for token in ("cache", "/tmp", "local path", "device id")):
            continue
        filtered.append(memory)

    return {
        "version": bundle.get("version", "1.0"),
        "source_agent": bundle.get("source_agent", "unknown-source"),
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "memories": filtered,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export transferable memories from a bundle or directly from local memory files."
    )
    parser.add_argument(
        "--source",
        required=True,
        help="Source bundle JSON, markdown/text file, or directory containing memory files",
    )
    parser.add_argument("--output", help="Optional output JSON file")
    parser.add_argument(
        "--types",
        nargs="*",
        help="Optional whitelist of memory types",
    )
    args = parser.parse_args()

    source_path = Path(args.source).expanduser().resolve()
    bundle = load_source_bundle(source_path)
    include_types = set(args.types) if args.types else None
    exported = filter_memories(bundle, include_types=include_types)

    payload = json.dumps(exported, indent=2)
    if args.output:
        output_path = Path(args.output).expanduser().resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)


if __name__ == "__main__":
    main()
