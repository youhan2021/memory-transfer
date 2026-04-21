from __future__ import annotations

import secrets
import string


def generate_transfer_id() -> str:
    return f"tr_{secrets.token_urlsafe(8)}"


def generate_short_code(length: int = 6) -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def build_qr_payload(transfer_id: str, short_code: str) -> str:
    return f"memory-transfer://fetch?transfer_id={transfer_id}&code={short_code}"
