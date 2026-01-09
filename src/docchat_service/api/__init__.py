# src/docchat_service/api/__init__.py (ПОЛНАЯ ВЕРСИЯ)
import contextlib
import typing as tp

from fastapi import FastAPI

from src.docchat_service.context import APP_CTX
from .middleware import log_requests
from .os_router import router as service_router
# ИСПРАВЛЕНО: правильный импорт роутера
from .v1.router import router as v1_router  # <-- КРИТИЧЕСКИ ВАЖНО: импортируем именно переменную router

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI) -> tp.AsyncGenerator[None, None]:
    await APP_CTX.on_startup()
    yield
    await APP_CTX.on_shutdown()

app_main = FastAPI(
    title="DocChat API",
    description="API для обработки документов и чата",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

app_main.middleware("http")(log_requests)
app_main.include_router(service_router, tags=["Service"])

app_main.include_router(v1_router)

__all__ = ["app_main"]