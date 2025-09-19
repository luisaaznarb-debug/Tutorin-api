from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
import os
from dotenv import load_dotenv
import json

# 🔹 Cargar variables de entorno
load_dotenv()

# 🔹 Inicializar FastAPI
app = FastAPI()

# 🔹 Cliente de OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 🔹 Datos de entrada
class ChatRequest(BaseModel):
    message: str  # lo que dice el niño
    grade: str = "5º"
    subject: str = "matemáticas"

# 🔹 Datos de salida
class Step(BaseModel):
    problem: str
    question: str
    answer: str
    hints: list[str]

class ChatResponse(BaseModel):
    steps: list[Step]

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    """
    Devuelve un plan paso a paso:
    - problem: el enunciado reformulado
    - question: la primera pregunta a resolver
    - answer: la respuesta esperada en ese paso
    - hints: lista de pistas progresivas
    """
    try:
        prompt = f"""
        Eres Tutorin, un profesor virtual para niños de primaria.
        El niño ha dicho: "{req.message}"
        Tema: {req.subject}, nivel: {req.grade}.

        Devuelve un JSON válido que contenga los pasos para resolver el problema.

        Formato:
        {{
          "steps": [
            {{
              "problem": "enunciado reformulado",
              "question": "primera pregunta a resolver",
              "answer": "respuesta esperada como texto corto",
              "hints": [
                "pista sencilla",
                "pista más detallada",
                "última pista revelando casi la respuesta"
              ]
            }}
          ]
        }}

        Importante:
        - Solo devuelve JSON válido.
        - Máximo 1 paso si el problema es simple.
        - Siempre incluye al menos 2 pistas en "hints".
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
        )

        raw = response.choices[0].message.content.strip()

        try:
            data = json.loads(raw)
        except Exception:
            return {"steps": [
                {
                    "problem": req.message,
                    "question": "Reformula tu problema.",
                    "answer": "no sé",
                    "hints": ["Intenta plantearlo de otra forma."]
                }
            ]}

        return data

    except Exception as e:
        return {"steps": [
            {
                "problem": req.message,
                "question": "Ocurrió un error",
                "answer": "error",
                "hints": [str(e)]
            }
        ]}
