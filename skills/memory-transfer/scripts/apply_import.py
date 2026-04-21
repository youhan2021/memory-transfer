#!/usr/bin/env python3
from __future__ import annotations

from copy import deepcopy


def apply_import(existing: list[dict], incoming: list[dict], mode: str) -> list[dict]:
    if mode == "replace":
        return deepcopy(incoming)
    if mode == "append":
        return deepcopy(existing) + deepcopy(incoming)
    if mode == "upsert":
        merged = {item["id"]: deepcopy(item) for item in existing}
        order = [item["id"] for item in existing]
        for item in incoming:
            item_id = item["id"]
            if item_id not in merged:
                order.append(item_id)
            merged[item_id] = deepcopy(item)
        return [merged[item_id] for item_id in order]
    raise ValueError(f"Unsupported import mode: {mode}")
