from datetime import datetime, timezone
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from . import schemas

router = APIRouter()

@router.get("/health", status_code=status.HTTP_200_OK, response_model=schemas.HealthResponse)
async def health():
    return {"status": "healthy"}

@router.get("/info", status_code=status.HTTP_200_OK, response_model=schemas.InfoResponse)
async def info():
    return {
        "name": "rag-document-processor",
        "version": "0.1.0",
        "description": "Local RAG system for document processing with Ollama"
    }

@router.get("/health/liveness", status_code=status.HTTP_200_OK)
async def liveness_probe():
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": "alive",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )

@router.get("/health/readiness", status_code=status.HTTP_200_OK)
async def readiness_probe():
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": "ready", "service": "rag-core"}
    )

__all__ = ["router"]