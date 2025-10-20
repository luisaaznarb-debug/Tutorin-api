from fastapi import APIRouter
from fastapi.responses import JSONResponse
from models import ChatRequest
from logic.utils import normalize_for_tts

# Si no quieres depender de ElevenLabs durante la depuración, devolvemos un "mock"
router = APIRouter()

@router.post("/")
def speak(request: ChatRequest):
    text = normalize_for_tts(request.message)
    # Mock: devolvemos URL “falsa” o texto
    return JSONResponse({"ok": True, "tts": f"[AUDIO_MOCK] {text}"})
