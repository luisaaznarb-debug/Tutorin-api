from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import openai
import os
from dotenv import load_dotenv

from tutorinskills import detectSkill, engine  # Importar funciones del módulo

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat")
async def chat(request: Request):
    try:
        body = await request.json()
        message = body.get("message", "")
        grade = body.get("grade", "")
        subject = body.get("subject", "")
        hint_mode = body.get("hintMode", "default")

        # Primero intentamos detectar una skill
        skill_key = detectSkill(message)

        if skill_key and skill_key in engine:
            steps = engine[skill_key](message)
            response_text = ""
            for i, step in enumerate(steps, 1):
                response_text += f"Paso {i}: {step.text}\n"
                if hint_mode == "pictograms" and step.imageUrl:
                    response_text += f"🖼️ {step.imageUrl}\n"
            return {"text": response_text.strip()}

        # Si no hay skill, usamos GPT-4o
        system_prompt = (
            "Eres Tutorín, un asistente virtual para niños de primaria. "
            "Explica de forma clara, paso a paso y con ejemplos fáciles. "
            "Si hintMode es 'pictograms', añade imágenes (ARASAAC) si puedes. "
            "Tu tono es cercano, claro y alegre."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Curso: {grade}\nAsignatura: {subject}\nPregunta: {message}"}
        ]

        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.6,
            max_tokens=800,
        )

        reply = response.choices[0].message.content
        return {"text": reply}

    except Exception as e:
        return {"error": str(e)}
