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
    ttl_seconds: int = Field(default=3600, ge=60, le=604800)
    consume_once: bool = True


class TransferCreateResponse(BaseModel):
    transfer_id: str
    expires_at: datetime
    short_code: str
    qr_payload: str
    consume_once: bool


class MemoryPreviewItem(BaseModel):
    id: str
    type: MemoryType
    title: str
    tags: list[str]
    sensitivity: Sensitivity


class BundlePreview(BaseModel):
    source_agent: str
    exported_at: datetime
    total_memories: int
    transferable_memories: int
    memories: list[MemoryPreviewItem]


class TransferFetchResponse(BaseModel):
    transfer_id: str
    expires_at: datetime
    consumed: bool
    preview: BundlePreview
    bundle: MemoryBundle | None = None


class TransferFetchRequest(BaseModel):
    transfer_id: str | None = None
    short_code: str | None = None
    code: str | None = None
    preview: bool = True


class ConsumeResponse(BaseModel):
    transfer_id: str
    consumed: bool
    consumed_at: datetime


class TransferRecord(BaseModel):
    transfer_id: str
    short_code: str
    bundle: MemoryBundle
    created_at: datetime
    expires_at: datetime
    consume_once: bool
    consumed: bool = False
    consumed_at: datetime | None = None

    def is_expired(self, now: datetime | None = None) -> bool:
        current = now or utc_now()
        return current >= self.expires_at

    def preview(self) -> BundlePreview:
        transferable_count = sum(1 for memory in self.bundle.memories if memory.transferable)
        return BundlePreview(
            source_agent=self.bundle.source_agent,
            exported_at=self.bundle.exported_at,
            total_memories=len(self.bundle.memories),
            transferable_memories=transferable_count,
            memories=[
                MemoryPreviewItem(
                    id=memory.id,
                    type=memory.type,
                    title=memory.title,
                    tags=memory.tags,
                    sensitivity=memory.sensitivity,
                )
                for memory in self.bundle.memories
            ],
        )
