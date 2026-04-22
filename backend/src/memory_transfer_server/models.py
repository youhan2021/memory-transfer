from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field


MemoryType = Literal[
    "preference",
    "profile",
    "project_context",
    "workflow",
    "tool_preference",
    "temporary",
]
Sensitivity = Literal["low", "medium", "high"]
ImportMode = Literal["append", "replace", "upsert"]
TransferStatus = Literal["pending", "consumed", "expired"]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class MemoryItem(BaseModel):
    id: str
    type: MemoryType
    title: str
    content: str
    tags: list[str] = Field(default_factory=list)
    transferable: bool
    sensitivity: Sensitivity


class MemoryBundle(BaseModel):
    version: str
    source_agent: str
    exported_at: datetime
    memories: list[MemoryItem] = Field(default_factory=list)


class TransferCreateRequest(BaseModel):
    bundle: MemoryBundle
    ttl_seconds: int = Field(default=600, ge=60, le=604800)


class TransferCreateResponse(BaseModel):
    transfer_id: str
    short_code: str
    confirm_phrase: str
    expires_at: datetime


class TransferPreview(BaseModel):
    source_agent: str
    exported_at: datetime
    expires_at: datetime
    memory_count: int
    memory_type_counts: dict[str, int]
    requires_confirm_phrase: bool = True


class TransferLookupRequest(BaseModel):
    short_code: str


class TransferFetchCompatRequest(BaseModel):
    short_code: str | None = None
    code: str | None = None


class TransferLookupResponse(BaseModel):
    transfer_id: str
    short_code: str
    status: TransferStatus
    preview: TransferPreview


class TransferConfirmImportRequest(BaseModel):
    short_code: str
    confirm_phrase: str
    import_mode: ImportMode = "upsert"


class TransferConfirmImportResponse(BaseModel):
    transfer_id: str
    short_code: str
    status: TransferStatus
    import_mode: ImportMode
    consumed_at: datetime
    bundle: MemoryBundle


class ConsumeResponse(BaseModel):
    transfer_id: str
    status: TransferStatus
    consumed_at: datetime


class TransferRecord(BaseModel):
    transfer_id: str
    short_code: str
    confirm_phrase: str
    status: TransferStatus = "pending"
    created_at: datetime
    expires_at: datetime
    consumed_at: datetime | None = None
    source_agent: str
    bundle: MemoryBundle

    def is_expired(self, now: datetime | None = None) -> bool:
        current = now or utc_now()
        return current >= self.expires_at

    def preview(self) -> TransferPreview:
        counts: dict[str, int] = {}
        for memory in self.bundle.memories:
            counts[memory.type] = counts.get(memory.type, 0) + 1
        return TransferPreview(
            source_agent=self.source_agent,
            exported_at=self.bundle.exported_at,
            expires_at=self.expires_at,
            memory_count=len(self.bundle.memories),
            memory_type_counts=counts,
            requires_confirm_phrase=True,
        )
