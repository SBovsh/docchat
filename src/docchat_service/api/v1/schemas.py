from pydantic import BaseModel
from typing import Optional, List, Dict

class HealthCheck(BaseModel):
    status: str = "ok"
    service: str = "docchat-v1"
    version: str = "1.0.0"


class DocumentUpload(BaseModel):
    filename: str
    size_bytes: int
    content_type: str


class DocumentUploadResponse(BaseModel):
    document_id: str
    message: str = "document upload succesfully"\


class ChatRequest(BaseModel):
    message: str
    mode: str = "general"
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str
    mode_used: str

__all__ = [
    "HealthCheck",
    "DocumentUpload",
    "DocumentUploadResponse",
    "ChatRequest",
    "ChatResponse"
]