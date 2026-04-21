#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib import request

from skill_config import get_server_url


def lookup_transfer(short_code: str) -> dict:
    server_url = get_server_url().rstrip("/")
    endpoint = f"{server_url}/transfer/lookup"
    payload = json.dumps({"short_code": short_code}).encode("utf-8")
    req = request.Request(
        endpoint,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(req) as response:
        return json.loads(response.read().decode("utf-8"))


def render_lookup_output(payload: dict) -> str:
    preview = payload["preview"]
    lines = [
        f"Found a memory bundle from {preview['source_agent']}.",
        "",
        "Includes:",
    ]
    for memory_type, count in sorted(preview["memory_type_counts"].items()):
        lines.append(f"- {count} {memory_type}")
    lines.extend(
        [
            "",
            f"Exported at: {preview['exported_at']}",
            f"Expires at: {preview['expires_at']}",
            "",
            "To continue, enter the confirm phrase.",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Lookup a transfer preview by short code.")
    parser.add_argument("--short-code", required=True, help="Human-readable short code")
    parser.add_argument("--format", choices=["prompt", "json"], default="prompt")
    parser.add_argument("--output", help="Optional output file for the response JSON")
    args = parser.parse_args()

    payload = lookup_transfer(args.short_code)
    if args.output:
        output_path = Path(args.output).expanduser().resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    if args.format == "json":
        print(json.dumps(payload, indent=2))
        return
    print(render_lookup_output(payload))


if __name__ == "__main__":
    main()
