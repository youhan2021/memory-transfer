#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
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


def post_create_transfer(
    bundle: dict,
    ttl_seconds: int,
    consume_once: bool,
) -> dict:
    server_url = get_server_url()
    endpoint = server_url.rstrip("/") + "/transfer/create"
    payload = json.dumps(
        {
            "bundle": bundle,
            "ttl_seconds": ttl_seconds,
            "consume_once": consume_once,
        }
    ).encode("utf-8")
    req = request.Request(
        endpoint,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(req) as response:
        return json.loads(response.read().decode("utf-8"))


def build_import_prompt(short_code: str | None, transfer_id: str | None) -> str:
    parts = [
        "请用 memory-transfer skill 从服务器拉取并导入这份记忆。",
        "先 preview，再用 upsert 模式导入。",
    ]
    if short_code:
        parts.insert(1, f"短码是 {short_code}。")
    elif transfer_id:
        parts.insert(1, f"transfer_id 是 {transfer_id}。")
    return " ".join(parts)


def select_output(payload: dict, output_kind: str) -> dict:
    short_import_prompt = build_import_prompt(
        short_code=payload["short_code"],
        transfer_id=None,
    )
    transfer_import_prompt = build_import_prompt(
        short_code=None,
        transfer_id=payload["transfer_id"],
    )
    prompts = {
        "import_by_short_code": short_import_prompt,
        "import_by_transfer_id": transfer_import_prompt,
    }
    prompt_bundle = {
        "send_to_target_agent": short_import_prompt,
        "import_by_short_code": short_import_prompt,
        "import_by_transfer_id": transfer_import_prompt,
    }
    if output_kind == "qr":
        return {
            "transfer_id": payload["transfer_id"],
            "qr_payload": payload["qr_payload"],
            "expires_at": payload["expires_at"],
            "next_prompts": prompt_bundle,
        }
    if output_kind == "short":
        return {
            "transfer_id": payload["transfer_id"],
            "short_code": payload["short_code"],
            "expires_at": payload["expires_at"],
            "next_prompts": prompt_bundle,
        }
    payload["next_prompts"] = prompt_bundle
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Upload a memory bundle to the configured server and return QR / short code transfer info."
    )
    parser.add_argument("--bundle", help="Existing bundle JSON file")
    parser.add_argument("--source", help="Source bundle JSON, markdown/text file, or directory")
    parser.add_argument("--output-kind", choices=["qr", "short", "both"], default="both")
    parser.add_argument("--ttl-seconds", type=int, default=3600)
    parser.add_argument("--types", nargs="*", help="Optional whitelist of memory types")
    parser.add_argument(
        "--consume-once",
        dest="consume_once",
        action="store_true",
        default=True,
        help="Mark transfer as one-time consumable (default)",
    )
    parser.add_argument(
        "--keep",
        dest="consume_once",
        action="store_false",
        help="Allow repeated fetch until TTL expiry",
    )
    args = parser.parse_args()

    if not args.bundle and not args.source:
        raise SystemExit("Either --bundle or --source is required.")

    bundle = build_bundle(args)
    response = post_create_transfer(
        bundle=bundle,
        ttl_seconds=args.ttl_seconds,
        consume_once=args.consume_once,
    )
    print(json.dumps(select_output(response, args.output_kind), indent=2))


if __name__ == "__main__":
    main()
