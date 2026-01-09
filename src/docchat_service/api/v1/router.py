from fastapi import APIRouter, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse
from .schemas import HealthCheck, DocumentUploadResponse, ChatResponse, ChatRequest
import uuid
import time

router = APIRouter(
    prefix="/api/v1",
    tags=["v1"],
    responses={404: {"description": "Not found"}},
)

@router.get("/health", response_model=HealthCheck, status_code=200)
async def health_check():
    return HealthCheck()

@router.post("/upload", response_model=ChatRequest, status_code=200)
async def upload(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException()

    document_id = str(uuid.uuid4())
    return DocumentUploadResponse(
        document_id=document_id,
        message=f"file {file.filename} uploaded",
    )


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    start_time = time.time()

    mode_used = request.mode or "general"
    session_id = request.session_id or str(uuid.uuid4())
    if request.message.lower() == "кто сейчас президент россии?":
        simulated_response = "Владимир Путин является действующим президентом Российской Федерации (по состоянию на 2024 год)."
    else:
        simulated_response = f"Это тестовый ответ в режиме '{mode_used}'. Ваш вопрос: '{request.message}'"
    elapsed = time.time() - start_time
    print(f"⏱Chat response time: {elapsed:.2f} seconds")
    return ChatResponse(
        response=simulated_response,
        session_id=session_id,
        mode_used=mode_used
    )