from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import openai
from tutorinskills import detectSkill, engine, Step

# Configura tu clave de OpenAI
openai.api_key = "TU_API_KEY"

# Inicializa la app
app = FastAPI()

# Permitir CORS (para conectar con tu frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelo de entrada
class SolveRequest(BaseModel):
    question: str
    grade: str
    subject: str

# Modelo de salida
class SolveResponse(BaseModel):
    steps: List[Step]

# Ruta principal para resolver
@app.post("/solve", response_model=SolveResponse)
async def solve(req: SolveRequest):
    skill = detectSkill(req.question)

    if skill and skill in engine:
        steps = engine[skill](req.question)
        return {"steps": steps}

    # Si no se detecta skill, usamos el modelo de lenguaje con rol system
    prompt = [
        {
            "role": "system",
            "content": f"Eres un profesor paciente y visual que ayuda a estudiantes de primaria (nivel {req.grade}) en el área de {req.subject}. Divide la respuesta en pasos simples y claros. Si puedes, incluye pictogramas (usa URLs de ARASAAC si aplica). Usa un lenguaje sencillo.",
        },
        {
            "role": "user",
            "content": req.question,
        },
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=prompt,
        temperature=0.7,
    )

    # Extraer y dividir la respuesta en pasos
    raw_answer = response['choices'][0]['message']['content']
    step_lines = [line.strip() for line in raw_answer.split("\n") if line.strip()]

    steps: List[Step] = []
    for line in step_lines:
        # Puedes usar una expresión regular para detectar URLs de imágenes si se incluye alguna
        if "http" in line:
            parts = line.split("http")
            steps.append(Step(text=parts[0].strip(), imageUrl="http" + parts[1].strip()))
        else:
            steps.append(Step(text=line))

    return {"steps": steps}
