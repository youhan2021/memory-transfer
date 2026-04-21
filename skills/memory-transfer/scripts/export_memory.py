#!/usr/bin/env python3
from __future__ import annotations

import argparse
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


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


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
    parser = argparse.ArgumentParser(description="Export transferable memories from a source bundle.")
    parser.add_argument("--source", required=True, help="Source JSON file")
    parser.add_argument("--output", help="Optional output JSON file")
    parser.add_argument(
        "--types",
        nargs="*",
        help="Optional whitelist of memory types",
    )
    args = parser.parse_args()

    source_path = Path(args.source).expanduser().resolve()
    bundle = load_json(source_path)
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
