from pydantic import BaseModel, Field

class HealthResponse(BaseModel):
    status: str = Field(default="healthy", description="Service health status")

class InfoResponse(BaseModel):
    name: str = Field(default="rag-document-processor")
    version: str = Field(default="0.1.0")
    description: str = Field(default="Local RAG system for document processing with Ollama")

class DocumentQuery(BaseModel):
    query: str = Field(..., description="Question about the document")
    document_ids: list[str] = Field(default_factory=list, description="List of document IDs to search")

class DocumentUploadResponse(BaseModel):
    document_id: str = Field(..., description="Unique ID for uploaded document")
    chunks_created: int = Field(..., description="Number of text chunks created")

__all__ = ["HealthResponse", "InfoResponse", "DocumentQuery", "DocumentUploadResponse"]