#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib import parse, request

from skill_config import get_server_url


def fetch_transfer(transfer_id: str | None, short_code: str | None, preview: bool) -> dict:
    server_url = get_server_url().rstrip("/")
    if transfer_id:
        endpoint = f"{server_url}/transfer/{parse.quote(transfer_id)}?preview={'true' if preview else 'false'}"
        req = request.Request(endpoint, method="GET")
    else:
        payload = json.dumps(
            {
                "short_code": short_code,
                "preview": preview,
            }
        ).encode("utf-8")
        endpoint = f"{server_url}/transfer/fetch"
        req = request.Request(
            endpoint,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

    with request.urlopen(req) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch a transfer by transfer_id or short_code from the configured backend."
    )
    parser.add_argument("--transfer-id", help="Transfer identifier")
    parser.add_argument("--short-code", help="Short code")
    parser.add_argument("--preview", action="store_true", help="Fetch preview only")
    parser.add_argument("--output", help="Optional output file for the response JSON")
    args = parser.parse_args()

    if not args.transfer_id and not args.short_code:
        raise SystemExit("Either --transfer-id or --short-code is required.")

    payload = fetch_transfer(
        transfer_id=args.transfer_id,
        short_code=args.short_code,
        preview=args.preview,
    )
    rendered = json.dumps(payload, indent=2)
    if args.output:
        output_path = Path(args.output).expanduser().resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
