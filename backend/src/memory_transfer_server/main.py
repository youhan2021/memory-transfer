from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from memory_transfer_server.config import get_settings
from memory_transfer_server.routes.health import router as health_router
from memory_transfer_server.routes.transfer import router as transfer_router
from memory_transfer_server.services.bundle_store import BundleStore
from memory_transfer_server.services.cleanup_service import run_cleanup
from memory_transfer_server.utils.logging import configure_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    app.state.settings = settings
    app.state.bundle_store = BundleStore(data_dir=settings.data_dir)
    run_cleanup(app.state.bundle_store)
    yield


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(
        title="memory-transfer-server",
        version="0.1.0",
        lifespan=lifespan,
        description="Temporary relay backend for selective agent memory transfer.",
    )
    app.include_router(health_router)
    app.include_router(transfer_router)
    return app


app = create_app()
