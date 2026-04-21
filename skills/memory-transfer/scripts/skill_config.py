#!/usr/bin/env python3
from __future__ import annotations

import os
from pathlib import Path


def _parse_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def load_skill_config() -> dict[str, str]:
    skill_dir = Path(__file__).resolve().parents[1]
    env_path = skill_dir / "config.env"
    config = _parse_env_file(env_path)

    server_url = os.getenv(
        "MEMORY_TRANSFER_SERVER_URL",
        config.get("MEMORY_TRANSFER_SERVER_URL", "http://127.0.0.1:8000/"),
    )

    return {
        "MEMORY_TRANSFER_SERVER_URL": server_url.rstrip("/") + "/",
    }


def get_server_url() -> str:
    return load_skill_config()["MEMORY_TRANSFER_SERVER_URL"]
