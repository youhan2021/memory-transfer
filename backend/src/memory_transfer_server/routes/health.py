from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/health")
def health(request: Request) -> dict[str, object]:
    store = request.app.state.bundle_store
    return {
        "status": "ok",
        "service": "memory-transfer-server",
        "active_transfers": store.active_count(),
    }
