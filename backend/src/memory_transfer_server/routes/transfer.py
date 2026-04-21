from fastapi import APIRouter, HTTPException, Request, status

from memory_transfer_server.models import (
    ConsumeResponse,
    TransferConfirmImportRequest,
    TransferConfirmImportResponse,
    TransferCreateRequest,
    TransferCreateResponse,
    TransferLookupRequest,
    TransferLookupResponse,
)
from memory_transfer_server.services.bundle_store import (
    TransferConfirmationError,
    TransferNotFoundError,
    TransferUnavailableError,
)

router = APIRouter(prefix="/transfer", tags=["transfer"])


@router.post("/create", response_model=TransferCreateResponse)
def create_transfer(
    payload: TransferCreateRequest,
    request: Request,
) -> TransferCreateResponse:
    store = request.app.state.bundle_store
    settings = request.app.state.settings
    ttl_seconds = min(payload.ttl_seconds, settings.max_ttl_seconds)
    normalized_payload = payload.model_copy(update={"ttl_seconds": ttl_seconds})
    return TransferCreateResponse(**store.create_transfer(normalized_payload))


@router.post("/lookup", response_model=TransferLookupResponse)
def lookup_transfer(
    payload: TransferLookupRequest,
    request: Request,
) -> TransferLookupResponse:
    store = request.app.state.bundle_store
    try:
        return store.lookup_transfer(payload.short_code)
    except TransferNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except TransferUnavailableError as exc:
        raise HTTPException(status_code=status.HTTP_410_GONE, detail=str(exc)) from exc


@router.post("/confirm-import", response_model=TransferConfirmImportResponse)
def confirm_import(
    payload: TransferConfirmImportRequest,
    request: Request,
) -> TransferConfirmImportResponse:
    store = request.app.state.bundle_store
    try:
        return store.confirm_import(payload)
    except TransferNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except TransferUnavailableError as exc:
        raise HTTPException(status_code=status.HTTP_410_GONE, detail=str(exc)) from exc
    except TransferConfirmationError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc


@router.post("/{transfer_id}/consume", response_model=ConsumeResponse)
def consume_transfer(transfer_id: str, request: Request) -> ConsumeResponse:
    store = request.app.state.bundle_store
    try:
        record = store.consume_transfer(transfer_id)
    except TransferNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except TransferUnavailableError as exc:
        raise HTTPException(status_code=status.HTTP_410_GONE, detail=str(exc)) from exc
    if record.consumed_at is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="consume operation failed",
        )
    return ConsumeResponse(
        transfer_id=record.transfer_id,
        status=record.status,
        consumed_at=record.consumed_at,
    )
