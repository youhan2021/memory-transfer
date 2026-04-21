#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a QR-friendly payload string.")
    parser.add_argument("--transfer-id", required=True, help="Transfer identifier")
    parser.add_argument("--short-code", required=True, help="Transfer short code")
    args = parser.parse_args()

    payload = f"memory-transfer://fetch?transfer_id={args.transfer_id}&code={args.short_code}"
    print(json.dumps({"qr_payload": payload, "ascii_qr_placeholder": f"[QR:{payload}]"}, indent=2))


if __name__ == "__main__":
    main()
