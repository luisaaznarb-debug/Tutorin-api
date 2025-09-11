# main.py  (Pydantic v1 compatible)

import os
import re
from typing import List, Optional, Dict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# OpenAI SDK v1
from openai import OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---------- Modelos ----------
class Step(BaseModel):
    text: str
    imageUrl: Optional[str] = None

class ChatRequest(BaseModel):
    # acepta ambos: "message" (nuevo) o "text" (legacy)
    text: Optional[str] = None
    message: Optional[str] = None
    grade: Optional[str] = "Primaria"
    history: Optional[List[Dict[str, str]]] = []

class ChatResponse(BaseModel):
    steps: List[Step]
    reply: Optional[str] = None

# ---------- App y CORS ----------
app = FastAPI(title="Tutorín API")

origins_env = os.getenv("FRONTEND_ORIGINS", "*")
allowed_origins = [o.strip() for o in origins_env.split(",")] if origins_env else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Utilidades ----------
def latexify(text: str) -> str:
    # 2/3 -> $\frac{2}{3}$
    text = re.sub(r"(?<!\d)(\d{1,3})\s*/\s*(\d{1,3})(?!\d)", r"$\\frac{\1}{\2}$", text)
    # x^2 -> x^{2}
    text = re.sub(r"([A-Za-z])\^(\d+)", r"\1^{\2}", text)
    # 3*4 -> 3 \times 4
    text = text.replace("*", " \\times ")
    return text

def to_steps(text: str) -> List[Step]:
    parts = re.split(r"\s*\d\)\s*", text)
    parts = [p.strip() for p in parts if p.strip()]
    if not parts:
        return [Step(text=text.strip())]
    return [Step(text=f"{i+1}) {p}") for i, p in enumerate(parts)]

SYSTEM_PROMPT = (
    "Eres Tutorín, un asistente para niños de primaria (6-12) en España. "
    "Explicas con lenguaje claro, amable y motivador. "
    "Nunca des la respuesta final de golpe: guía por PISTAS y preguntas. "
    "Estructura: 1) Relee el enunciado; 2) Pista 1; 3) Pista 2; 4) Pregunta. "
    "Usa LaTeX entre $...$ o $$...$$ en fracciones y fórmulas "
    "(2/3 -> $\\frac{2}{3}$, 3*4 -> 3\\times4, x^2 -> $x^{2}$)."
)

# ---------- Rutas ----------
@app.get("/ping")
def ping():
    return {"ok": True, "message": "Tutorín está vivo 👋"}

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(status_code=500, detail="Falta OPENAI_API_KEY en el servidor.")

    user_message = (req.message or req.text or "").strip()
    grade = (req.grade or "Primaria").strip()

    if not user_message:
        raise HTTPException(status_code=400, detail="El campo 'message'/'text' está vacío.")

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for turn in (req.history or []):
        r, c = turn.get("role", ""), turn.get("content", "")
        if r in {"user", "assistant"} and c:
            messages.append({"role": r, "content": c})
    messages.append({
        "role": "user",
        "content": (
            f"Curso/etapa: {grade}. "
            f"Enunciado o duda del niño: {user_message}. "
            "Guía por pasos numerados y termina con una pregunta."
        ),
    })

    try:
        completion = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=0.2,
            messages=messages,
        )
        reply = (completion.choices[0].message.content or "").strip()
        if not reply:
            raise RuntimeError("Respuesta vacía del modelo.")

        reply_fmt = latexify(reply)
        steps = to_steps(reply_fmt)
        return ChatResponse(steps=steps, reply=reply_fmt)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando pistas: {e}")

# Local: uvicorn main:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")), reload=True)