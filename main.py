from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

# === MODELOS DE DATOS ===

class Step(BaseModel):
    type: str
    content: str

class ChatRequest(BaseModel):
    question: str
    history: Optional[List[str]] = None

class ChatResponse(BaseModel):
    steps: List[Step]
    audioUrl: Optional[str] = None

# === INICIALIZACIÓN ===

app = FastAPI()

# Orígenes permitidos (puedes controlar con variable de entorno FRONTEND_ORIGINS)
origins = [
    "http://localhost:3000",
    "https://tutorintuprofesvirtual.netlify.app",
    "https://tutorin-web.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === PROMPT BASE ===
SYSTEM_PROMPT = (
    "Eres Tutorín, un asistente educativo para niños de 6 a 12 años. "
    "Solo das pistas paso a paso, no das la respuesta final de golpe. "
    "Usa frases cortas, tono paciente y motivador. "
    "Si el niño se bloquea, anímale y ofrécele una micro-pista. "
    "Siempre terminas con una pregunta. "
    "Nunca divagues fuera del ejercicio."
)

# === ENDPOINTS ===

@app.get("/ping")
def ping():
    return {"message": "Tutorín está vivo 👋"}

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    """
    Aquí iría tu lógica real:
    - Pasar la pregunta + historial a GPT
    - Generar steps[] = [{type: "text", content: "..."}]
    - (Opcional) llamar a ElevenLabs para audioUrl
    """
    steps = [
        Step(type="text", content="¡Bien! Vamos a resolverlo paso a paso."),
        Step(type="text", content="Primero piensa: ¿qué operación hay que hacer? 🤔")
    ]
    return ChatResponse(steps=steps)

# === ALIAS PARA COMPATIBILIDAD ===

@app.post("/solve", response_model=ChatResponse)
def solve(req: ChatRequest):
    return chat(req)
