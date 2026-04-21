from __future__ import annotations

import json
from datetime import timedelta
from pathlib import Path

from memory_transfer_server.models import (
    MemoryBundle,
    TransferCreateRequest,
    TransferFetchResponse,
    TransferRecord,
    utc_now,
)
from memory_transfer_server.services.token_service import (
    build_qr_payload,
    generate_short_code,
    generate_transfer_id,
)


class TransferNotFoundError(KeyError):
    pass


class TransferUnavailableError(RuntimeError):
    pass


class BundleStore:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._records: dict[str, TransferRecord] = {}

    def create_transfer(self, request: TransferCreateRequest) -> dict[str, object]:
        now = utc_now()
        transfer_id = generate_transfer_id()
        short_code = generate_short_code()
        record = TransferRecord(
            transfer_id=transfer_id,
            short_code=short_code,
            bundle=request.bundle,
            created_at=now,
            expires_at=now + timedelta(seconds=request.ttl_seconds),
            consume_once=request.consume_once,
        )
        self._records[transfer_id] = record
        self._persist_record(record)
        return {
            "transfer_id": transfer_id,
            "expires_at": record.expires_at,
            "short_code": short_code,
            "qr_payload": build_qr_payload(transfer_id, short_code),
            "consume_once": record.consume_once,
        }

    def fetch_transfer(self, transfer_id: str, preview_only: bool = True) -> TransferFetchResponse:
        record = self._get_active_record(transfer_id)
        return TransferFetchResponse(
            transfer_id=record.transfer_id,
            expires_at=record.expires_at,
            consumed=record.consumed,
            preview=record.preview(),
            bundle=None if preview_only else record.bundle,
        )

    def fetch_transfer_by_short_code(
        self,
        short_code: str,
        preview_only: bool = True,
    ) -> TransferFetchResponse:
        record = self._get_active_record_by_short_code(short_code)
        return TransferFetchResponse(
            transfer_id=record.transfer_id,
            expires_at=record.expires_at,
            consumed=record.consumed,
            preview=record.preview(),
            bundle=None if preview_only else record.bundle,
        )

    def consume_transfer(self, transfer_id: str) -> TransferRecord:
        record = self._get_active_record(transfer_id, allow_consumed=True)
        if not record.consumed:
            record.consumed = True
            record.consumed_at = utc_now()
            self._persist_record(record)
        return record

    def cleanup_expired(self) -> int:
        expired_ids = [
            transfer_id
            for transfer_id, record in self._records.items()
            if record.is_expired()
        ]
        for transfer_id in expired_ids:
            del self._records[transfer_id]
            snapshot = self.data_dir / f"{transfer_id}.json"
            if snapshot.exists():
                snapshot.unlink()
        return len(expired_ids)

    def active_count(self) -> int:
        self.cleanup_expired()
        return len(self._records)

    def _get_active_record(
        self,
        transfer_id: str,
        allow_consumed: bool = False,
    ) -> TransferRecord:
        self.cleanup_expired()
        record = self._records.get(transfer_id)
        if record is None:
            raise TransferNotFoundError(f"transfer {transfer_id} not found")
        if record.consume_once and record.consumed and not allow_consumed:
            raise TransferUnavailableError(f"transfer {transfer_id} already consumed")
        return record

    def _get_active_record_by_short_code(
        self,
        short_code: str,
        allow_consumed: bool = False,
    ) -> TransferRecord:
        self.cleanup_expired()
        for record in self._records.values():
            if record.short_code == short_code:
                if record.consume_once and record.consumed and not allow_consumed:
                    raise TransferUnavailableError(
                        f"transfer with short code {short_code} already consumed"
                    )
                return record
        raise TransferNotFoundError(f"transfer with short code {short_code} not found")

    def _persist_record(self, record: TransferRecord) -> None:
        snapshot_path = self.data_dir / f"{record.transfer_id}.json"
        snapshot_path.write_text(
            json.dumps(record.model_dump(mode="json"), indent=2),
            encoding="utf-8",
        )
