from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
import os
from dotenv import load_dotenv
import base64
import requests

# 🚀 Cargar variables de entorno
load_dotenv()

# Inicializar cliente OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Clave ElevenLabs
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "jw7ksPllnpL2oNWqa0Jl")  # 👈 voz fija que pediste

app = FastAPI()


# 📌 Modelos
class ChatMessage(BaseModel):
    role: str   # "Niño" | "Tutorin"
    content: str

class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    subject: str
    grade: str

class ChatResponse(BaseModel):
    reply: str

class TTSRequest(BaseModel):
    text: str

class TTSResponse(BaseModel):
    audio: str   # base64


# 📌 Chat dinámico
@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """
    Tutorín dinámico: confirma problema, da pistas, corrige y avanza paso a paso.
    """

    history = []
    for m in req.messages:
        if m.role == "Niño":
            history.append({"role": "user", "content": m.content})
        else:
            history.append({"role": "assistant", "content": m.content})

    system_instruction = f"""
Eres Tutorín, un profesor virtual paciente para niños de primaria.
Nivel: {req.grade}, asignatura: {req.subject}.

Reglas:
1. Si el niño plantea un problema, repítelo con tus palabras y da una primera pista.
2. Cuando el niño responde:
   - Si es correcto, avanza al siguiente paso de la resolución.
   - Si es incorrecto o dice "no sé", da una pista adicional sobre el mismo paso (NO avances aún).
3. No des toda la solución de golpe. Ve paso a paso.
4. Usa frases cortas, claras, motivadoras y en español.
5. Sé amable y anima al niño.
"""

    conversation = [{"role": "system", "content": system_instruction}] + history

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=conversation,
        temperature=0.7,
    )

    reply = response.choices[0].message.content
    return {"reply": reply}


# 📌 TTS con ElevenLabs
@app.post("/tts", response_model=TTSResponse)
async def tts(req: TTSRequest):
    """
    Convierte texto en voz usando ElevenLabs y devuelve el audio en base64.
    """

    if not ELEVENLABS_API_KEY:
        return {"audio": "", "error": "Falta ELEVENLABS_API_KEY en variables de entorno"}

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"

    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
    }

    payload = {
        "text": req.text,
        "voice_settings": {
            "stability": 0.6,
            "similarity_boost": 0.8
        }
    }

    try:
        resp = requests.post(url, headers=headers, json=payload)
        resp.raise_for_status()

        audio_bytes = resp.content
        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")

        return {"audio": audio_b64}
    except Exception as e:
        return {"audio": "", "error": str(e)}
