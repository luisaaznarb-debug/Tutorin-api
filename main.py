from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
from fastapi.middleware.cors import CORSMiddleware
import os
import json
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configurar FastAPI
app = FastAPI()

# Habilitar CORS (para que el frontend pueda llamar sin error)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ en producción mejor restringir a tu dominio
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cliente de OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ----- Modelos -----
class ChatMessage(BaseModel):
    role: str  # "Niño" | "Tutorin"
    text: str

class ChatRequest(BaseModel):
    message: str
    grade: str = "5º"
    subject: str = "matemáticas"

class CoachBlock(BaseModel):
    type: str  # "Pregunta" | "Pista" | "Respuesta" | "Pista extra"
    text: str

class CoachResponse(BaseModel):
    blocks: list[CoachBlock]

# ----- Endpoints -----
@app.get("/")
def root():
    return {"message": "Tutorin API funcionando 🚀"}

@app.post("/chat", response_model=CoachResponse)
def chat(req: ChatRequest):
    """
    Genera bloques estructurados: Pregunta, Pista, Respuesta...
    """
    try:
        prompt = f"""
        Eres Tutorin, un profesor virtual paciente y amable para niños de primaria.
        El niño te ha dicho: "{req.message}".
        Tema: {req.subject}, nivel: {req.grade}.

        Devuelve SOLO un JSON con este formato exacto:

        {{
          "blocks": [
            {{
              "type": "Pregunta",
              "text": "Reformula el problema en forma de pregunta inicial"
            }},
            {{
              "type": "Pista",
              "text": "Primera pista sencilla"
            }},
            {{
              "type": "Respuesta",
              "text": "Respuesta final esperada, clara y corta"
            }},
            {{
              "type": "Pista extra",
              "text": "Consejo o explicación adicional para aprender mejor"
            }}
          ]
        }}
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
        )

        raw = response.choices[0].message.content.strip()
        print("🔎 RAW RESPONSE:", raw)

        # Intentar parsear JSON
        data = json.loads(raw)
        return data

    except Exception as e:
        return {
            "blocks": [
                {"type": "Pregunta", "text": "Ha ocurrido un error."},
                {"type": "Pista", "text": str(e)},
            ]
        }
