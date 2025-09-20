from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import openai
import requests
from dotenv import load_dotenv
import base64

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")

app = FastAPI()

# 🔧 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # en producción cámbialo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔹 Saludo inicial fijo
INITIAL_GREETING = "¡Hola! Soy Tutorín, tu profe virtual. ¿En qué te puedo ayudar hoy?"

@app.get("/greet")
async def greet():
    reply_text = INITIAL_GREETING
    audio_base64 = synthesize_audio(reply_text)
    return {"reply": reply_text, "audio": audio_base64}

# 🔹 Endpoint de chat
@app.post("/chat")
async def chat(payload: dict):
    messages = payload.get("messages", [])
    subject = payload.get("subject", "matemáticas")
    grade = payload.get("grade", "primaria")

    # GPT genera respuesta
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": f"Eres Tutorín, un profesor de {subject} para {grade}. "
                                          "No des la respuesta directamente, primero ofrece pistas. "
                                          "Si el alumno responde, valida su respuesta (si es correcta, felicítalo; "
                                          "si es incorrecta, da más pistas)."},
            *messages,
        ],
    )

    reply_text = response.choices[0].message["content"]

    # ElevenLabs genera audio solo del texto final
    audio_base64 = synthesize_audio(reply_text)

    return {"reply": reply_text, "audio": audio_base64}

# 🔹 Función auxiliar para generar audio
def synthesize_audio(text: str):
    if not ELEVENLABS_API_KEY or not ELEVENLABS_VOICE_ID:
        return None

    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
    }
    tts_response = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}",
        headers=headers,
        json={"text": text, "voice_settings": {"stability": 0.4, "similarity_boost": 0.8}},
    )

    if tts_response.status_code == 200:
        return base64.b64encode(tts_response.content).decode("utf-8")
    return None
