from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
import os
from dotenv import load_dotenv

# 🚀 Cargar variables desde .env
load_dotenv()

# Inicializar cliente OpenAI con la clave del entorno
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()


# 📌 Modelos
class ChatMessage(BaseModel):
    role: str  # "Niño" | "Tutorin"
    content: str

class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    subject: str
    grade: str
    maxHints: int | None = 3

class CoachBlock(BaseModel):
    type: str  # "Pregunta" | "Pista" | "Respuesta" | "Pista extra"
    text: str

class CoachResponse(BaseModel):
    blocks: list[CoachBlock]


# 📌 Endpoint principal
@app.post("/chat", response_model=CoachResponse)
async def chat(req: ChatRequest):
    """
    Genera un ejercicio educativo paso a paso en español,
    devolviendo bloques con etiquetas:
    - Pregunta
    - Pista
    - Respuesta
    - Pista extra
    """

    conversation = [
        {
            "role": "system",
            "content": f"""
Eres Tutorín, un tutor virtual para niños de primaria (grado {req.grade}).
Materia: {req.subject}.

Tu tarea es devolver un problema paso a paso en formato JSON.
Cada paso debe estar etiquetado como:
- "Pregunta" (el enunciado principal)
- "Pista" (una ayuda para resolver)
- "Pista extra" (ayuda adicional si el niño no responde bien)
- "Respuesta" (el resultado correcto al final)

Ejemplo de salida:
{{
  "blocks": [
    {{"type": "Pregunta", "text": "¿Cuánto es 12 + 8?"}},
    {{"type": "Pista", "text": "Intenta sumar primero las decenas"}},
    {{"type": "Pista extra", "text": "12 + 8 = 20"}},
    {{"type": "Respuesta", "text": "La respuesta es 20"}}
  ]
}}
Devuelve solo JSON válido, sin explicaciones adicionales.
"""
        },
        {
            "role": "user",
            "content": f"Genera un problema de {req.subject} para un niño de {req.grade}."
        },
    ]

    # 📌 Llamada a OpenAI
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=conversation,
        temperature=0.6,
    )

    raw_text = response.choices[0].message.content

    import json
    try:
        data = json.loads(raw_text)
    except Exception:
        # fallback si el modelo no devuelve JSON válido
        data = {
            "blocks": [
                {"type": "Pregunta", "text": "¿Cuánto es 5 + 3?"},
                {"type": "Pista", "text": "Cuenta con los dedos"},
                {"type": "Pista extra", "text": "5 + 3 = 8"},
                {"type": "Respuesta", "text": "La respuesta es 8"}
            ]
        }

    return data
