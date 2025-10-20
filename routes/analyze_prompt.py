# -*- coding: utf-8 -*-
"""
routes/analyze_prompt.py
---------------------------------
Endpoint de análisis del texto o voz del alumno.
Detecta materia, tema, motor y etiquetas NLU
sin añadir respuestas automáticas.
"""

from fastapi import APIRouter, UploadFile, Form
from pydantic import BaseModel
from typing import Optional
import io

from modules.ai_analyzer import analyze_prompt
# Si en el futuro reactivas el audio:
# from modules.audio_utils import speech_to_text

router = APIRouter()


# -------------------------------------------------------
# MODELOS DE PETICIÓN
# -------------------------------------------------------
class TextRequest(BaseModel):
    text: str


# -------------------------------------------------------
# ENDPOINTS
# -------------------------------------------------------

@router.post("/text")
def analyze_text(req: TextRequest):
    """
    Analiza un texto del alumno.
    Detecta tema, materia y motor (NLU).
    """
    result = analyze_prompt(req.text or "")
    return {
        "input": req.text,
        "nlu": result
    }


@router.post("/voice")
async def analyze_voice(file: UploadFile, cycle: Optional[str] = Form("c2")):
    """
    Analiza un archivo de voz.
    Convierte a texto y detecta materia, motor y etiquetas NLU.
    """
    # --- Si quieres reactivar el audio ---
    # content = await file.read()
    # text = speech_to_text(io.BytesIO(content))
    # result = analyze_prompt(text or "")
    # return {"input": text, "nlu": result, "cycle": cycle}

    # --- Temporalmente desactivado (modo texto) ---
    return {
        "message": "🔇 El análisis por voz está desactivado temporalmente.",
        "cycle": cycle
    }
