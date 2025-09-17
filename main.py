import os
import re
import math
from typing import List, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from tutorinSkills import engine, detectSkill, Step as SkillStep

# =========================
# Configuración & CORS
# =========================
def _origins_from_env() -> List[str]:
    raw = os.getenv("FRONTEND_ORIGINS", "")
    items = [x.strip() for x in raw.split(",") if x.strip()]
    if not items:
        items = ["http://localhost:3000"]
    return items

app = FastAPI(title="Tutorín API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins_from_env(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# Modelos
# =========================
class Step(BaseModel):
    text: str
    imageUrl: Optional[str] = None

class ChatRequest(BaseModel):
    message: Optional[str] = None
    question: Optional[str] = None
    grade: Optional[str] = None
    history: Optional[List[str]] = None

class ChatResponse(BaseModel):
    steps: List[Step]
    audioUrl: Optional[str] = None

# =========================
# Endpoint principal
# =========================
@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    user_text = (req.message or req.question or "").strip()

    # Buscar skill automática
    skill_id = detectSkill(user_text)
    if skill_id and skill_id in engine:
        raw_steps = engine[skill_id](user_text)
        steps = [Step(text=s.text, imageUrl=s.imageUrl) for s in raw_steps]
        return ChatResponse(steps=steps)

    # Fallback básico si no encuentra
    fallback = [
        Step(text="Vamos a resolverlo paso a paso, pero no estoy seguro del tema."),
        Step(text="¿Puedes darme un poco más de detalle sobre tu pregunta? 🧐"),
    ]
    return ChatResponse(steps=fallback)

@app.post("/solve", response_model=ChatResponse)
def solve(req: ChatRequest):
    return chat(req)

@app.get("/ping")
def ping():
    return {"status": "ok", "name": "Tutorín está vivo 👋"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")), reload=True)
