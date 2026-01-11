# src/docchat_service/api/v1/router.py

from fastapi import APIRouter, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse
from .schemas import HealthCheck, DocumentUploadResponse, ChatResponse, ChatRequest
import uuid
import time
from .service import process_uploaded_file  # ← импортируем новую функцию

router = APIRouter(
    prefix="/api/v1",
    tags=["v1"],
    responses={404: {"description": "Not found"}},
)

@router.get("/health", response_model=HealthCheck, status_code=200)
async def health_check():
    return HealthCheck()

@router.post("/upload", response_model=DocumentUploadResponse, status_code=200)
async def upload(file: UploadFile = File(...)):
    """
    Загружает файл, обрабатывает его и возвращает document_id + результат.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Файл не указан")

    try:
        result = await process_uploaded_file(file)
        return DocumentUploadResponse(
            document_id=result["document_id"],
            message=result["message"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка обработки файла: {str(e)}")


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