from dotenv import load_dotenv
from pathlib import Path
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
from openai import OpenAI

# --- Cargar variables .env ---
ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=ENV_PATH, override=True)

# --- App FastAPI ---
app = FastAPI(title="Tutorín API", version="0.1.0")

from fastapi.middleware.cors import CORSMiddleware

# Orígenes permitidos (frontend en local + futuro Vercel)
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://*.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Endpoint de prueba ---
@app.get("/ping")
def ping():
    return {"ok": True, "message": "Tutorín está vivo 👋"}

# --- Cliente OpenAI ---
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- Modelos de datos ---
class ChatRequest(BaseModel):
    message: str
    grade: Optional[str] = "Primaria"
    history: Optional[List[Dict[str, str]]] = []

class ChatResponse(BaseModel):
    reply: str

# --- Prompt pedagógico ---
SYSTEM_PROMPT = (
    "Eres Tutorín, un asistente para niños de primaria (6-12) en España. "
    "Siempre explicas con lenguaje claro y amable. "
    "Nunca das la respuesta final directamente: guías con PISTAS y preguntas. "
    "Estructura: 1) Relee el enunciado; 2) Pista 1; 3) Pista 2; 4) Pregunta al niño. "
    "Cuando uses matemáticas, escribe fórmulas en LaTeX entre $...$ o $$...$$. "
    "Sé breve, positivo y motivador."
)

# --- Endpoint /chat ---
@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    if not os.getenv("OPENAI_API_KEY"):
        return ChatResponse(reply="Configura OPENAI_API_KEY en el servidor.")

    # Construir historial
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for m in (req.history or []):
        if m.get("role") in ("user", "assistant"):
            messages.append({"role": m["role"], "content": m["content"]})
    messages.append({"role": "user", "content": req.message})

    # Llamada al modelo GPT
    completion = client.chat.completions.create(
        model="gpt-4o-mini",   # puedes usar "gpt-4o-mini" si quieres abaratar
        messages=messages,
        temperature=0.4,
        max_tokens=400,
    )
    reply = completion.choices[0].message.content.strip()
    return ChatResponse(reply=reply)
