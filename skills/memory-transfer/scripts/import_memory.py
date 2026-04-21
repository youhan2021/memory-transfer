#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from apply_import import apply_import


def load_bundle(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_target(path: Path) -> list[dict]:
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        return payload.get("memories", [])
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Import a memory bundle into a local target file.")
    parser.add_argument("--bundle", required=True, help="Path to bundle JSON")
    parser.add_argument("--target", required=True, help="Path to target JSON file")
    parser.add_argument(
        "--mode",
        default="upsert",
        choices=["append", "replace", "upsert"],
        help="Import mode",
    )
    args = parser.parse_args()

    bundle_path = Path(args.bundle).expanduser().resolve()
    target_path = Path(args.target).expanduser().resolve()

    bundle = load_bundle(bundle_path)
    incoming = bundle.get("memories", [])
    existing = load_target(target_path)
    merged = apply_import(existing, incoming, args.mode)

    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(json.dumps({"memories": merged}, indent=2) + "\n", encoding="utf-8")

    print(
        json.dumps(
            {
                "target": str(target_path),
                "mode": args.mode,
                "existing_count": len(existing),
                "incoming_count": len(incoming),
                "result_count": len(merged),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
