# src/spr_test/api/middleware.py
import time
import uuid
from datetime import datetime

from fastapi import Request
from starlette.concurrency import iterate_in_threadpool

from src.docchat_service.context import APP_CTX

NON_LOGGED_ENDPOINTS = ("/health", "/health/liveness", "/health/readiness", "/info", "/openapi.json", "/docs")


async def log_requests(request: Request, call_next):
    start_time = time.time()
    logger = APP_CTX.get_logger()
    request_path = request.url.path
    trace_id = request.headers.get("X-Request-Id", str(uuid.uuid4()))
    APP_CTX.get_context_vars_container().set_trace_id(trace_id)
    if request_path not in NON_LOGGED_ENDPOINTS:
        logger.info(f"Incoming {request.method} {request_path}", extra={
            "trace_id": trace_id,
            "path": request_path,
            "client": request.client.host if request.client else "unknown"
        })

    response = await call_next(request)
    processing_time_ms = int((time.time() - start_time) * 1000)
    if request_path not in NON_LOGGED_ENDPOINTS:
        logger.info(f"Completed {request_path} in {processing_time_ms}ms", extra={
            "trace_id": trace_id,
            "status": response.status_code,
            "duration_ms": processing_time_ms
        })

    response.headers["X-Request-Id"] = trace_id
    return response


__all__ = ["log_requests"]