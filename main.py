import os
import re
import math
from typing import List, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


# =========================
# Configuración & CORS
# =========================
def _origins_from_env() -> List[str]:
    raw = os.getenv("FRONTEND_ORIGINS", "")
    items = [x.strip() for x in raw.split(",") if x.strip()]
    # valores útiles por defecto en local
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
    type: str = "text"
    content: str


class ChatRequest(BaseModel):
    # Nota: el front te envía "message"; mantenemos compatibilidad
   message: Optional[str] = None
   question: Optional[str] = None
   grade: Optional[str] = None
   history: Optional[List[str]] = None


class ChatResponse(BaseModel):
    steps: List[Step]
    audioUrl: Optional[str] = None


# =========================
# Utilidades de fracciones
# =========================

# Palabras comunes -> denominador
SPANISH_DENOMS = {
    "mitad": 2, "mitades": 2,
    "medio": 2, "medios": 2, "media": 2, "medias": 2,
    "tercio": 3, "tercios": 3, "tercia": 3, "tercias": 3,
    "cuarto": 4, "cuartos": 4, "cuarta": 4, "cuartas": 4,
    "quinto": 5, "quintos": 5, "quinta": 5, "quintas": 5,
    "sexto": 6, "sextos": 6, "sexta": 6, "sextas": 6,
    "séptimo": 7, "septimo": 7, "séptimos": 7, "septimos": 7,
    "séptima": 7, "septima": 7, "séptimas": 7, "septimas": 7,
    "octavo": 8, "octavos": 8, "octava": 8, "octavas": 8,
    "noveno": 9, "novenos": 9, "novena": 9, "novenas": 9,
    "décimo": 10, "decimo": 10, "décimos": 10, "decimos": 10,
    "décima": 10, "decima": 10, "décimas": 10, "decimas": 10,
}

NUM_WORDS = {
    # por si algún día llega en palabras (opcional)
    "uno": 1, "una": 1, "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5,
    "seis": 6, "siete": 7, "ocho": 8, "nueve": 9, "diez": 10,
}


def normalize_spanish_fractions(txt: str) -> str:
    """
    Convierte expresiones como:
      '4 octavos' -> '4/8'
      '3 cuartos' -> '3/4'
      'dos tercios' -> '2/3' (si vienen en palabras)
    y también normaliza conectores 'más'/'menos' a +/-
    """
    s = txt or ""
    # normaliza signos
    s = re.sub(r"\b(m[aá]s)\b", "+", s, flags=re.IGNORECASE)
    s = re.sub(r"\bmenos\b", "-", s, flags=re.IGNORECASE)

    # números en palabras (muy básico)
    def _num_word_to_digit(m: re.Match) -> str:
        w = m.group(0).lower()
        return str(NUM_WORDS.get(w, w))
    s = re.sub(r"\b(uno|una|dos|tres|cuatro|cinco|seis|siete|ocho|nueve|diez)\b",
               _num_word_to_digit, s, flags=re.IGNORECASE)

    # (n) (denominador-en-palabras) -> n/den
    # ejemplo: "4 octavos" => "4/8"
    for w, d in SPANISH_DENOMS.items():
        s = re.sub(rf"\b(\d+)\s+{w}\b", lambda m: f"{m.group(1)}/{d}", s, flags=re.IGNORECASE)

    # limpia dobles espacios
    s = re.sub(r"\s{2,}", " ", s).strip()
    return s


def parse_fraction_expression(s: str):
    """
    Devuelve (a,b,op,c,d) si encuentra 'a/b (+|-) c/d', o None si no.
    """
    pat = re.compile(
        r"(?P<a>\d+)\s*/\s*(?P<b>\d+)\s*(?P<op>[+\-])\s*(?P<c>\d+)\s*/\s*(?P<d>\d+)"
    )
    m = pat.search(s)
    if not m:
        return None
    a = int(m.group("a"))
    b = int(m.group("b"))
    c = int(m.group("c"))
    d = int(m.group("d"))
    op = m.group("op")
    return a, b, op, c, d


def gcd(a: int, b: int) -> int:
    return math.gcd(a, b)


def lcm(a: int, b: int) -> int:
    return abs(a * b) // gcd(a, b) if a and b else 0


def simplify(n: int, d: int):
    if d == 0:
        return n, d
    g = gcd(abs(n), abs(d))
    return n // g, d // g


def build_fraction_steps(a: int, b: int, op: str, c: int, d: int) -> List[Step]:
    """
    Genera PISTAS para suma/resta de fracciones con distinto o igual denominador.
    Siempre acaba con una PREGUNTA abierta para aprendizaje activo.
    """
    steps: List[Step] = []
    emoji = "🤔"

    # 0) saludo breve
    steps.append(Step(content="¡Bien! Vamos a resolverlo paso a paso."))

    if b == d:
        # mismo denominador
        steps.append(
            Step(content=f"Pista 1: Los denominadores ya son iguales ({b}). "
                         f"Solo trabaja con los numeradores. ¿Qué numerador obtienes al {('sumar' if op=='+' else 'restar')} {a} y {c}? {emoji}")
        )
        return steps

    # distinto denominador
    m = lcm(b, d)
    steps.append(
        Step(content=f"Pista 1: Busca el MCM de {b} y {d}. ¿Cuál es el MCM? {emoji}")
    )
    steps.append(
        Step(content=f"Pista 2: Convierte ambas fracciones al denominador común {m}. "
                     f"¿Qué numeradores quedan para {a}/{b} y {c}/{d}? {emoji}")
    )
    steps.append(
        Step(content=f"Pista 3: Ahora {('suma' if op=='+' else 'resta')} los numeradores que obtuviste. "
                     f"¿Qué resultado te da antes de simplificar? {emoji}")
    )
    steps.append(
        Step(content="Pista 4: Si puedes, simplifica la fracción final dividiendo numerador y denominador "
                     "por su máximo común divisor. ¿Cuál es la fracción simplificada? ✨")
    )
    return steps


# =========================
# Endpoints
# =========================
@app.get("/ping")
def ping():
    return {"status": "ok", "name": "Tutorín está vivo 👋"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    """
    Flujo mínimo:
      - Normaliza texto (p.ej. '4 octavos' -> '4/8')
      - Si detecta suma/resta de fracciones: devuelve PISTAS
      - Si no, guía genérica (una sola pista + pregunta)
    """
    user_text = (req.message or req.question or "").strip()
    norm = normalize_spanish_fractions(user_text)

    parsed = parse_fraction_expression(norm)
    if parsed:
        a, b, op, c, d = parsed
        steps = build_fraction_steps(a, b, op, c, d)
        return ChatResponse(steps=steps)

    # Fallback pedagógico genérico
    steps = [
        Step(content="¡Bien! Vamos a resolverlo paso a paso."),
        Step(content="Primero piensa: ¿qué operación hay que hacer? 🤔"),
    ]
    return ChatResponse(steps=steps)


# Alias para compatibilidad con el front si apunta a /solve
@app.post("/solve", response_model=ChatResponse)
def solve(req: ChatRequest):
    return chat(req)


# Ejecutar en local:  uvicorn main:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")), reload=True)
