#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Preview a memory bundle.")
    parser.add_argument("--bundle", required=True, help="Bundle JSON file")
    args = parser.parse_args()

    bundle_path = Path(args.bundle).expanduser().resolve()
    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    memories = bundle.get("memories", [])

    preview = {
        "source_agent": bundle.get("source_agent"),
        "exported_at": bundle.get("exported_at"),
        "total_memories": len(memories),
        "types": sorted({memory.get("type") for memory in memories}),
        "memories": [
            {
                "id": memory.get("id"),
                "type": memory.get("type"),
                "title": memory.get("title"),
                "sensitivity": memory.get("sensitivity"),
            }
            for memory in memories
        ],
    }
    print(json.dumps(preview, indent=2))


if __name__ == "__main__":
    main()
