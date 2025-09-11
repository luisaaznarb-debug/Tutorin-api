import os
import re
from typing import List, Optional, Dict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ConfigDict

# --- OpenAI client (SDK v1) ---
try:
    from openai import OpenAI
except Exception as e:
    raise RuntimeError(
        "Falta el paquete 'openai'. Instala: pip install openai>=1.0.0"
    ) from e

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---------------- Pydantic models ----------------

class Step(BaseModel):
    text: str
    imageUrl: Optional[str] = None

class ChatRequest(BaseModel):
    # Acepta "message" (oficial) y también "text" como alias por compatibilidad
    message: str = Field(validation_alias="text")
    grade: Optional[str] = "Primaria"
    history: Optional[List[Dict[str, str]]] = []

    # Ignora campos extra para no romperse si el front manda algo más
    model_config = ConfigDict(extra="ignore")

class ChatResponse(BaseModel):
    steps: List[Step]
    reply: Optional[str] = None  # Texto completo, por si lo necesitas

# ---------------- FastAPI app & CORS ----------------

app = FastAPI(title="Tutorín API")

# CORS: permite tu dominio de Netlify; si no se define, permite todos (desarrollo)
origins_env = os.getenv("FRONTEND_ORIGINS", "*")
allowed_origins = [o.strip() for o in origins_env.split(",")] if origins_env else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- Utilidades de formateo ----------------

def latexify(text: str) -> str:
    """
    Convierte fracciones y multiplicaciones simples a LaTeX:
      2/3 -> $\frac{2}{3}$, 3*4 -> 3 \times 4, x^2 -> x^{2}
    (Heurística ligera para respuestas de primaria)
    """
    # fracciones a/b con 1-3 dígitos a cada lado, sin números pegados alrededor
    text = re.sub(r"(?<!\d)(\d{1,3})\s*/\s*(\d{1,3})(?!\d)", r"$\\frac{\1}{\2}$", text)
    # potencias tipo x^2 -> x^{2}
    text = re.sub(r"([A-Za-z])\^(\d+)", r"\1^{\2}", text)
    # multiplicación con asterisco -> \times (sin tocar rutas tipo /path)
    text = text.replace("*", " \\times ")
    return text

def to_steps(text: str) -> List[Step]:
    """
    Separa "1) ... 2) ... 3) ..." en una lista de pasos.
    Si no encuentra patrón, devuelve el texto entero como un solo paso.
    """
    parts = re.split(r"\s*\d\)\s*", text)
    parts = [p.strip() for p in parts if p.strip()]
    if not parts:
        return [Step(text=text.strip())]
    return [Step(text=f"{i+1}) {p}") for i, p in enumerate(parts)]

# ---------------- Prompt del sistema ----------------

SYSTEM_PROMPT = (
    "Eres Tutorín, un asistente para niños de primaria (6-12) en España. "
    "Explicas con lenguaje claro, amable y motivador. "
    "NUNCA des la respuesta final de golpe: guías por PISTAS y preguntas. "
    "Estructura: 1) Relee el enunciado; 2) Pista 1; 3) Pista 2; 4) Pregunta para que el niño avance. "
    "Cuando aparezcan fórmulas o fracciones, usa LaTeX entre $...$ o $$...$$. "
    "Ejemplos: 2/3 -> $\\frac{2}{3}$, 3*4 -> 3\\times4, x^2 -> $x^{2}$. "
    "Sé breve, positivo y motivador."
)

# ---------------- Rutas ----------------

@app.get("/ping")
def ping():
    return {"ok": True, "message": "Tutorín está vivo 👋"}

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(
            status_code=500,
            detail="Falta OPENAI_API_KEY en el servidor."
        )

    user_message = req.message.strip()
    grade = (req.grade or "Primaria").strip()

    if not user_message:
        raise HTTPException(status_code=400, detail="El campo 'message' está vacío.")

    # Mensajes (incluye historial si te interesa conservar el contexto)
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    # Si recibes historial del front, puedes incorporarlo aquí:
    for turn in (req.history or []):
        r = turn.get("role", "")
        c = turn.get("content", "")
        if r in {"user", "assistant"} and c:
            messages.append({"role": r, "content": c})

    messages.append({
        "role": "user",
        "content": (
            f"Curso/etapa: {grade}. "
            f"Enunciado o duda del niño: {user_message}. "
            "Recuerda: guía por pasos con números y termina con una pregunta para que participe."
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
        # Devuelve el error al front para depurar desde la UI
        raise HTTPException(status_code=500, detail=f"Error generando pistas: {e}")

# --------- Si quieres ejecutar en local: uvicorn main:app --reload ----------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=True,
    )
