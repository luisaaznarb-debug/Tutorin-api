import os
import re
from typing import List, Optional, Dict, Tuple

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---------- Modelos ----------
class Step(BaseModel):
    text: str
    imageUrl: Optional[str] = None

class ChatRequest(BaseModel):
    # acepta ambas claves desde el front
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

# ---------- Utilidades de LaTeX y pasos ----------
def latexify(text: str) -> str:
    text = re.sub(r"(?<!\d)(\d{1,3})\s*/\s*(\d{1,3})(?!\d)", r"$\\frac{\1}{\2}$", text)
    text = re.sub(r"([A-Za-z])\s*\^\s*(\d+)", r"\1^{\2}", text)
    text = text.replace("*", " \\times ")
    return text

def to_steps(text: str) -> List[Step]:
    parts = re.split(r"\s*\d\)\s*", text)
    parts = [p.strip() for p in parts if p.strip()]
    if not parts:
        return [Step(text=text.strip())]
    return [Step(text=f"{i+1}) {p}") for i, p in enumerate(parts)]

# ---------- Guard-rails matemáticos (fracciones simples) ----------
def gcd(a: int, b: int) -> int:
    while b:
        a, b = b, a % b
    return abs(a)

def lcm(a: int, b: int) -> int:
    return abs(a * b) // gcd(a, b) if a and b else 0

def extract_fractions(expr: str) -> List[Tuple[int, int]]:
    # captura fracciones tipo a/b (1-3 dígitos)
    return [(int(a), int(b)) for a, b in re.findall(r"(?<!\d)(\d{1,3})\s*/\s*(\d{1,3})(?!\d)", expr)]

def math_hints(user_text: str) -> str:
    fracs = extract_fractions(user_text)
    if len(fracs) >= 2 and any(op in user_text for op in ["+", "-"]):
        denoms = [b for (_, b) in fracs[:2]]
        nums = [a for (a, _) in fracs[:2]]
        m = lcm(denoms[0], denoms[1])
        if m:
            eq_nums = [nums[i] * (m // denoms[i]) for i in range(2)]
            sign = "+" if "+" in user_text and "-" not in user_text else "-"
            return (
                f"FRACCIONES_DETECTADAS={fracs[:2]}; MCM={m}; "
                f"EQUIVALENCIAS=({eq_nums[0]}/{m}) {sign} ({eq_nums[1]}/{m}). "
                "USA ESTOS DATOS COMO GUÍA, PERO EXPLÍCALO AL NIÑO EN PASOS."
            )
    return ""

# ---------- Prompt del sistema (estricto) ----------
SYSTEM_PROMPT = (
    "Eres Tutorín, un asistente para niños de primaria (6-12) en España.\n"
    "REGLAS PEDAGÓGICAS:\n"
    "- CIÑETE AL ENUNCIADO. No inventes números ni temas que no aparezcan.\n"
    "- Si hay operaciones con fracciones escritas con '/', guía al niño: "
    "  1) encontrar el denominador común (MCM), 2) convertir a ese denominador, "
    "  3) operar numeradores, 4) simplificar si procede.\n"
    "- Usa LaTeX entre $...$ o $$...$$ en fórmulas: 2/3->$\\frac{2}{3}$, 3*4->3\\times4, x^2->$x^{2}$.\n"
    "- Formato de salida OBLIGATORIO: pasos numerados '1) ... 2) ... 3) ...' con frases cortas "
    "  y UNA sola pregunta al final para que el niño responda.\n"
    "- No incluyas contenidos ajenos (p. ej., par/impar) salvo que el enunciado lo pida.\n"
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

    # pistas técnicas (no visibles para el niño)
    hints = math_hints(user_message)

    # Mensajes para el modelo
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for turn in (req.history or []):
        r, c = turn.get("role", ""), turn.get("content", "")
        if r in {"user", "assistant"} and c:
            messages.append({"role": r, "content": c})
    # Enunciado del alumno + recordatorio de formato + pistas internas
    user_block = (
        f"Curso: {grade}.\n"
        f"Enunciado del alumno (cópialo tal cual en el primer paso): {user_message}\n"
        "Devuelve SOLO pasos numerados y termina con UNA pregunta.\n"
    )
    if hints:
        user_block += f"\n[NOTAS INTERNAS PARA EL TUTOR — NO LEER NI MOSTRAR]: {hints}"

    messages.append({"role": "user", "content": user_block})

    try:
        completion = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=0.1,
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
