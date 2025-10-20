# -*- coding: utf-8 -*-
"""
Modules/audio_utils.py
Genera o transcribe audio para Tutorín.
Entrada: voz del alumno (Whisper opcional)
Salida: voz del asistente (gTTS en español)
"""

import io
import os
import re
import base64

# --- STT (voz a texto) con OpenAI Whisper opcional ---
try:
    from openai import OpenAI
    _oa_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) if os.getenv("OPENAI_API_KEY") else None
except Exception:
    _oa_client = None

# --- TTS (texto a voz) con Google Text-to-Speech ---
try:
    from gtts import gTTS
except Exception:
    gTTS = None


# ============================================================
# 🧹 Función de limpieza HTML
# ============================================================
def clean_html_tags(text: str) -> str:
    """
    Limpia etiquetas HTML y convierte fracciones visuales en lenguaje natural.
    """
    if not text:
        return ""

    # 1️⃣ Detectar fracciones en formato HTML tipo <div>2</div><div style=...>3</div>
    # Sustituir por expresiones tipo “dos tercios”
    text = re.sub(
        r"<div[^>]*>(\d+)</div>\s*<div[^>]*>(\d+)</div>",
        r"\1 entre \2",
        text
    )

    # 2️⃣ Eliminar cualquier etiqueta HTML restante
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"&[a-zA-Z#0-9]+;", " ", text)

    # 3️⃣ Sustituir símbolos por lenguaje natural
    text = (
        text.replace("×", " por ")
            .replace("·", " por ")
            .replace("÷", " entre ")
            .replace("/", " entre ")
            .replace(":", " entre ")
            .replace("+", " más ")
            .replace("-", " menos ")
            .replace("=", " igual a ")
    )

    # 4️⃣ Limpiar espacios extra
    text = re.sub(r"\s+", " ", text).strip()
    return text

# ============================================================
# 🎤 Transcripción de audio → texto
# ============================================================
def speech_to_text(audio_path: str, language_code: str = "es") -> str:
    """
    Convierte voz en texto (usa Whisper si hay API_KEY).
    """
    if _oa_client and os.path.exists(audio_path):
        try:
            with open(audio_path, "rb") as f:
                result = _oa_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=f
                )
            return (result.text or "").strip()
        except Exception as e:
            print("⚠️ Error Whisper:", e)
    return ""


# ============================================================
# 🔊 Texto → audio (en base64)
# ============================================================
def text_to_speech_b64(text: str, lang: str = "es") -> str:
    """
    Convierte texto en audio mp3 codificado en base64.
    Limpia etiquetas HTML y caracteres especiales antes del TTS.
    """
    if not text:
        return ""
    if gTTS is None:
        print("⚠️ gTTS no está disponible, no se generará audio.")
        return ""

    try:
        # 🧹 Limpieza del texto para que el TTS no lea HTML
        clean_text = clean_html_tags(text)

        # 🎙️ Generación de audio con gTTS
        tts = gTTS(text=clean_text, lang=lang)
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        buf.seek(0)

        # 🔄 Codificación en base64
        encoded = base64.b64encode(buf.read()).decode("utf-8")
        return encoded

    except Exception as e:
        print("❌ Error en text_to_speech_b64:", e)
        return ""
