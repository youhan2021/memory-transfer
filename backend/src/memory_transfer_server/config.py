from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class Settings:
    data_dir: Path
    default_ttl_seconds: int = 3600
    max_ttl_seconds: int = 604800
    consume_once_default: bool = True


def get_settings() -> Settings:
    root_dir = Path(__file__).resolve().parents[3]
    data_dir_value = os.getenv("MEMORY_TRANSFER_DATA_DIR", ".data")
    data_dir = Path(data_dir_value)
    if not data_dir.is_absolute():
        data_dir = root_dir / data_dir

    return Settings(
        data_dir=data_dir,
        default_ttl_seconds=int(
            os.getenv("MEMORY_TRANSFER_DEFAULT_TTL_SECONDS", "3600")
        ),
        max_ttl_seconds=int(os.getenv("MEMORY_TRANSFER_MAX_TTL_SECONDS", "604800")),
        consume_once_default=os.getenv(
            "MEMORY_TRANSFER_CONSUME_ONCE_DEFAULT", "true"
        ).lower()
        in {"1", "true", "yes"},
    )
