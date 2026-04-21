from __future__ import annotations

from memory_transfer_server.services.bundle_store import BundleStore


def run_cleanup(store: BundleStore) -> int:
    return store.cleanup_expired()
