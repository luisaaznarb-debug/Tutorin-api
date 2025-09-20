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

# 🔧 CORS para permitir frontend (localhost:3000 o Netlify)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # en producción cámbialo a ["https://tusitio.netlify.app"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/chat")
async def chat(payload: dict):
    messages = payload.get("messages", [])
    subject = payload.get("subject", "matemáticas")
    grade = payload.get("grade", "primaria")

    # 🔹 GPT genera respuesta con enfoque de pistas
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": f"""
Eres Tutorín, un profesor de {subject} para {grade}.
Tu misión es guiar al niño paso a paso:
1. Siempre responde primero con una pista o una pregunta sencilla que ayude a razonar.
2. Solo si el niño responde mal varias veces o pide la solución explícita, das la respuesta completa.
3. Usa un tono motivador, claro y breve, como un profesor paciente.
""",
            },
            *messages,
        ],
    )

    reply_text = response.choices[0].message["content"]

    # 🔹 ElevenLabs genera audio
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
    }
    tts_response = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}",
        headers=headers,
        json={
            "text": reply_text,
            "voice_settings": {"stability": 0.4, "similarity_boost": 0.8},
        },
    )

    audio_base64 = None
    if tts_response.status_code == 200:
        audio_base64 = base64.b64encode(tts_response.content).decode("utf-8")

    return {"reply": reply_text, "audio": audio_base64}
