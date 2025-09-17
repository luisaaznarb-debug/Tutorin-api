import os
from typing import List, Literal, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("⚠️ Falta OPENAI_API_KEY en variables de entorno.")
client = OpenAI(api_key=OPENAI_API_KEY)

app = FastAPI(title="Tutorin API", version="0.1.0")

# CORS abierto para desarrollo; en producción restringe dominios
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==== Esquemas ====
class Message(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str

class CoachBlock(BaseModel):
    type: Literal["question", "hint", "answer"]
    text: str

class CoachResponse(BaseModel):
    blocks: List[CoachBlock]

class ChatBody(BaseModel):
    messages: List[Message]
    subject: Optional[str] = "general"
    grade: Optional[str] = "3º"
    mode: Optional[Literal["coach"]] = "coach"
    max_hints: Optional[int] = 2

@app.get("/ping")
def ping():
    return {"ok": True}

# ==== Helper: prompt de sistema ====
SYSTEM_PROMPT = """Eres Tutorin, un profesor paciente para niños de primaria.
Responde SIEMPRE en español neutro. Tu estilo:
- Claro, breve y amable.
- No des sermones.
- Evita tecnicismos innecesarios.
- Usa números pequeños, ejemplos sencillos.

Tu salida DEBE ser un JSON con este formato:
{
  "blocks": [
    {"type":"question","text":"..."},
    {"type":"hint","text":"..."},
    {"type":"answer","text":"..."},
    {"type":"hint","text":"..."}  // este último hint es opcional
  ]
}

Reglas:
- `question`: replantea lo que el niño pregunta, en una frase.
- `hint`: guía sin revelar la solución (piensa en pasos).
- `answer`: da el resultado final y un mínimo de explicación (1-2 frases).
- Longitud máxima por bloque: 220 caracteres.
- Usa el nivel indicado para ajustar vocabulario.
"""

def build_user_prompt(messages: List[Message], subject: str, grade: str, max_hints: int):
    last_user = next((m.content for m in reversed(messages) if m.role == "user"), "")
    return f"""Asignatura: {subject}
Nivel/curso: {grade}
Número de pistas: {max_hints}

Pregunta del niño: {last_user}"""

@app.post("/chat", response_model=CoachResponse)
def chat(body: ChatBody):
    if body.mode != "coach":
        raise HTTPException(status_code=400, detail="Modo no soportado. Usa mode='coach'.")

    if not OPENAI_API_KEY:
        # Fallback de emergencia si no hay API key
        demo = CoachResponse(blocks=[
            CoachBlock(type="question", text="¿Cómo sumar fracciones como 1/2 + 3/4?"),
            CoachBlock(type="hint", text="Busca un denominador común."),
            CoachBlock(type="answer", text="1/2 + 3/4 = 5/4 = 1,25."),
            CoachBlock(type="hint", text="Convierte a décimales si te ayuda."),
        ])
        return demo

    user_prompt = build_user_prompt(body.messages, body.subject or "general", body.grade or "3º", body.max_hints or 2)

    try:
        # Forzamos JSON estructurado usando response_format con schema
        schema = {
            "name": "coach_schema",
            "schema": {
                "type": "object",
                "properties": {
                    "blocks": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "type": {"type":"string","enum":["question","hint","answer"]},
                                "text": {"type":"string"}
                            },
                            "required": ["type","text"],
                            "additionalProperties": False
                        },
                        "minItems": 2,
                        "maxItems": 6
                    }
                },
                "required": ["blocks"],
                "additionalProperties": False
            },
            "strict": True
        }

        chat = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role":"system","content": SYSTEM_PROMPT},
                {"role":"user","content": user_prompt},
            ],
            response_format={"type": "json_schema", "json_schema": schema},
            temperature=0.6,
        )

        import json
        data = json.loads(chat.choices[0].message.content)
        # Validación ligera
        blocks_in = data.get("blocks", [])
        blocks: List[CoachBlock] = []
        for b in blocks_in:
            t = b.get("type")
            txt = b.get("text","").strip()
            if t in ("question","hint","answer") and txt:
                blocks.append(CoachBlock(type=t, text=txt))
        if not blocks:
            raise ValueError("Respuesta sin bloques")
        return CoachResponse(blocks=blocks)
    except Exception as e:
        print("LLM error:", e)
        raise HTTPException(status_code=500, detail="Error generando respuesta.")
