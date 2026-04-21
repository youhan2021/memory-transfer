#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from urllib import request

from export_memory import filter_memories, load_source_bundle
from skill_config import get_server_url


def load_bundle(bundle_path: Path) -> dict:
    return json.loads(bundle_path.read_text(encoding="utf-8"))


def build_bundle(args: argparse.Namespace) -> dict:
    include_types = set(args.types) if args.types else None
    if args.bundle:
        bundle = load_bundle(Path(args.bundle).expanduser().resolve())
    else:
        bundle = load_source_bundle(Path(args.source).expanduser().resolve())
    return filter_memories(bundle, include_types=include_types)


def post_create_transfer(bundle: dict, ttl_seconds: int) -> dict:
    server_url = get_server_url()
    endpoint = server_url.rstrip("/") + "/transfer/create"
    payload = json.dumps({"bundle": bundle, "ttl_seconds": ttl_seconds}).encode("utf-8")
    req = request.Request(
        endpoint,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(req) as response:
        return json.loads(response.read().decode("utf-8"))


def summarize_bundle(bundle: dict) -> list[str]:
    counts = Counter(memory.get("type", "unknown") for memory in bundle.get("memories", []))
    return [f"- {count} {memory_type}" for memory_type, count in sorted(counts.items())]


def render_prompt_output(payload: dict, bundle: dict) -> str:
    lines = [
        "Transfer ready.",
        "",
        f"Code: {payload['short_code']}",
        f"Transfer ID: {payload['transfer_id']}",
        f"Confirm phrase: {payload['confirm_phrase']}",
        f"Expires at: {payload['expires_at']}",
        "",
        "Includes:",
    ]
    lines.extend(summarize_bundle(bundle) or ["- 0 memories"])
    lines.append("")
    lines.append("Send this to the target agent:")
    lines.append(
        "请用 memory-transfer skill 先 lookup 这份记忆。"
        f"短码是 {payload['short_code']}。"
        "拿到 preview 后，要求我输入 confirm phrase。"
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create a transfer session and return short code plus confirm phrase."
    )
    parser.add_argument("--bundle", help="Existing bundle JSON file")
    parser.add_argument("--source", help="Source bundle JSON, markdown/text file, or directory")
    parser.add_argument("--ttl-seconds", type=int, default=600)
    parser.add_argument("--types", nargs="*", help="Optional whitelist of memory types")
    parser.add_argument(
        "--format",
        choices=["prompt", "json"],
        default="prompt",
        help="Render a fixed human-facing prompt block or JSON payload",
    )
    args = parser.parse_args()

    if not args.bundle and not args.source:
        raise SystemExit("Either --bundle or --source is required.")

    bundle = build_bundle(args)
    response = post_create_transfer(bundle=bundle, ttl_seconds=args.ttl_seconds)
    if args.format == "json":
        rendered = dict(response)
        rendered["memory_type_counts"] = dict(
            Counter(memory.get("type", "unknown") for memory in bundle.get("memories", []))
        )
        print(json.dumps(rendered, indent=2))
        return
    print(render_prompt_output(response, bundle))


if __name__ == "__main__":
    main()
