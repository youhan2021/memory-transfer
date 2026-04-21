#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from urllib import request

from import_memory import import_bundle_to_target
from skill_config import get_server_url


def confirm_import(short_code: str, confirm_phrase: str, import_mode: str) -> dict:
    server_url = get_server_url().rstrip("/")
    endpoint = f"{server_url}/transfer/confirm-import"
    payload = json.dumps(
        {
            "short_code": short_code,
            "confirm_phrase": confirm_phrase,
            "import_mode": import_mode,
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


def render_prompt_output(response: dict, summary: dict) -> str:
    return "\n".join(
        [
            "Import completed.",
            "",
            f"Short Code: {response['short_code']}",
            f"Status: {response['status']}",
            f"Import mode: {summary['mode']}",
            f"Imported memories: {summary['result_count']}",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Confirm a transfer with short code plus confirm phrase, then import locally."
    )
    parser.add_argument("--short-code", required=True, help="Human-readable short code")
    parser.add_argument("--confirm-phrase", required=True, help="Two-word confirm phrase")
    parser.add_argument("--target", required=True, help="Target JSON file or target directory")
    parser.add_argument(
        "--mode",
        default="upsert",
        choices=["append", "replace", "upsert"],
        help="Import mode",
    )
    parser.add_argument("--format", choices=["prompt", "json"], default="prompt")
    args = parser.parse_args()

    response = confirm_import(args.short_code, args.confirm_phrase, args.mode)
    summary = import_bundle_to_target(response["bundle"], args.target, args.mode)
    rendered = {
        "transfer_id": response["transfer_id"],
        "short_code": response["short_code"],
        "status": response["status"],
        "consumed_at": response["consumed_at"],
        **summary,
    }
    if args.format == "json":
        print(json.dumps(rendered, indent=2))
        return
    print(render_prompt_output(response, summary))


if __name__ == "__main__":
    main()
