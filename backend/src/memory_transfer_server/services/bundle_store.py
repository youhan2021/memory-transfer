from __future__ import annotations

import json
from datetime import timedelta
from pathlib import Path

from memory_transfer_server.models import (
    TransferConfirmImportRequest,
    TransferConfirmImportResponse,
    TransferCreateRequest,
    TransferLookupResponse,
    TransferRecord,
    utc_now,
)
from memory_transfer_server.services.token_service import (
    generate_confirm_phrase,
    generate_short_code,
    generate_transfer_id,
)


class TransferNotFoundError(KeyError):
    pass


class TransferUnavailableError(RuntimeError):
    pass


class TransferConfirmationError(ValueError):
    pass


class BundleStore:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._records: dict[str, TransferRecord] = {}

    def create_transfer(self, request: TransferCreateRequest) -> dict[str, object]:
        now = utc_now()
        record = TransferRecord(
            transfer_id=self._unique_transfer_id(),
            short_code=self._unique_short_code(),
            confirm_phrase=generate_confirm_phrase(),
            created_at=now,
            expires_at=now + timedelta(seconds=request.ttl_seconds),
            source_agent=request.bundle.source_agent,
            bundle=request.bundle,
        )
        self._records[record.transfer_id] = record
        self._persist_record(record)
        return {
            "transfer_id": record.transfer_id,
            "short_code": record.short_code,
            "confirm_phrase": record.confirm_phrase,
            "expires_at": record.expires_at,
        }

    def lookup_transfer(self, short_code: str) -> TransferLookupResponse:
        record = self._get_pending_record_by_short_code(short_code)
        return TransferLookupResponse(
            transfer_id=record.transfer_id,
            short_code=record.short_code,
            status=record.status,
            preview=record.preview(),
        )

    def confirm_import(
        self,
        request: TransferConfirmImportRequest,
    ) -> TransferConfirmImportResponse:
        record = self._get_pending_record_by_short_code(request.short_code)
        if record.confirm_phrase != request.confirm_phrase:
            raise TransferConfirmationError("confirm phrase did not match")

        record.status = "consumed"
        record.consumed_at = utc_now()
        self._persist_record(record)
        return TransferConfirmImportResponse(
            transfer_id=record.transfer_id,
            short_code=record.short_code,
            status=record.status,
            import_mode=request.import_mode,
            consumed_at=record.consumed_at,
            bundle=record.bundle,
        )

    def consume_transfer(self, transfer_id: str) -> TransferRecord:
        record = self._get_record(transfer_id)
        if record.status == "consumed" and record.consumed_at is not None:
            return record
        if record.is_expired():
            record.status = "expired"
            self._persist_record(record)
            raise TransferUnavailableError(f"transfer {transfer_id} expired")

        record.status = "consumed"
        record.consumed_at = utc_now()
        self._persist_record(record)
        return record

    def cleanup_expired(self) -> int:
        updated = 0
        for record in self._records.values():
            if record.status == "pending" and record.is_expired():
                record.status = "expired"
                self._persist_record(record)
                updated += 1
        return updated

    def active_count(self) -> int:
        self.cleanup_expired()
        return sum(1 for record in self._records.values() if record.status == "pending")

    def _unique_transfer_id(self) -> str:
        while True:
            candidate = generate_transfer_id()
            if candidate not in self._records:
                return candidate

    def _unique_short_code(self) -> str:
        existing_codes = {record.short_code for record in self._records.values()}
        while True:
            candidate = generate_short_code()
            if candidate not in existing_codes:
                return candidate

    def _get_record(self, transfer_id: str) -> TransferRecord:
        self.cleanup_expired()
        record = self._records.get(transfer_id)
        if record is None:
            raise TransferNotFoundError(f"transfer {transfer_id} not found")
        return record

    def _get_pending_record_by_short_code(self, short_code: str) -> TransferRecord:
        self.cleanup_expired()
        for record in self._records.values():
            if record.short_code != short_code:
                continue
            if record.status == "expired":
                raise TransferUnavailableError(f"transfer with short code {short_code} expired")
            if record.status == "consumed":
                raise TransferUnavailableError(f"transfer with short code {short_code} already consumed")
            return record
        raise TransferNotFoundError(f"transfer with short code {short_code} not found")

    def _persist_record(self, record: TransferRecord) -> None:
        snapshot_path = self.data_dir / f"{record.transfer_id}.json"
        snapshot_path.write_text(
            json.dumps(record.model_dump(mode="json"), indent=2),
            encoding="utf-8",
        )
