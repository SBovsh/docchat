import contextlib
import typing as tp

from fastapi import FastAPI

from src.docchat_service.context import APP_CTX

from .middleware import log_requests
from .os_router import router as service_router
from .v1 import router

@contextlib.asynccontextmanager
async def lifespan(_) -> tp.AsyncContextManager:
    await APP_CTX.on_startup()
    yield
    await APP_CTX.on_shutdown()

app_main = FastAPI(title="RAG Document Processor", lifespan=lifespan)
app_main.middleware("http")(log_requests)
app_main.include_router(service_router, tags=["Service routes"])
app_main.include_router(router, prefix="/api/v1", tags=["RAG API"])

__all__ = ["app_main"]