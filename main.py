import os
import re
from typing import List, Optional, Dict, Tuple

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI

# ---------- OpenAI ----------
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---------- Modelos ----------
class Step(BaseModel):
    text: str
    imageUrl: Optional[str] = None

class ChatRequest(BaseModel):
    text: Optional[str] = None
    message: Optional[str] = None
    grade: Optional[str] = "Primaria"
    history: Optional[List[Dict[str, str]]] = []

class ChatResponse(BaseModel):
    steps: List[Step]
    reply: Optional[str] = None

# ---------- App & CORS ----------
app = FastAPI(title="Tutorín API (6º Primaria)")
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
def gcd(a: int, b: int) -> int:
    while b: a, b = b, a % b
    return abs(a)

def lcm(a: int, b: int) -> int:
    return abs(a*b)//gcd(a,b) if a and b else 0

def ints(s: str) -> List[int]:
    return [int(x) for x in re.findall(r"-?\d+", s)]

def last_turn(history: List[Dict[str,str]], role: str) -> Optional[Dict[str,str]]:
    for t in reversed(history or []):
        if t.get("role")==role and t.get("content"): return t
    return None

# LaTeX seguro: no rompe **negritas**, fuerza ×/÷ en matemático
def latexify(t: str) -> str:
    # Fracciones "a/b" simples (no URLs)
    t = re.sub(r"(?<!\d)(\d{1,3})\s*/\s*(\d{1,3})(?!\d)", r"$\\frac{\1}{\2}$", t)
    # Potencias x^n
    t = re.sub(r"([A-Za-z])\s*\^\s*(\d+)", r"\1^{\2}", t)
    # * como multiplicación (pero no **negritas**)
    t = re.sub(r"(?<!\*)\*(?!\*)", r" $\\times$ ", t)
    # \times suelto -> matemático
    t = re.sub(r"\\times", r"$\\times$", t)
    # ÷ -> LaTeX
    t = t.replace("÷", " $\\div$ ")
    return t

def steps_only(text: str) -> List[Step]:
    parts = re.split(r"\s*\d\)\s*", text)
    parts = [p.strip() for p in parts if p.strip()]
    if not parts: return [Step(text=text.strip())]
    return [Step(text=f"{i+1}) {p}") for i,p in enumerate(parts)]

# ---------- Detecciones ----------
ADD_RE = re.compile(r"\b(\d{1,6})\s*(?:\+|más)\s*(\d{1,6})\b")
SUB_RE = re.compile(r"\b(\d{1,6})\s*(?:-|menos)\s*(\d{1,6})\b")
MUL_RE = re.compile(r"\b(\d{1,6})\s*(?:×|x|\*)\s*(\d{1,4})\b")
DIV_RE = re.compile(r"\b(\d{1,8})\s*(?:÷|:|\/)\s*(\d{1,4})\b")
FRAC2_RE = re.compile(r"(?<!\d)(\d{1,3})\s*/\s*(\d{1,3})\s*([+-])\s*(\d{1,3})\s*/\s*(\d{1,3})(?!\d)")
FRAC_MUL_DIV_RE = re.compile(r"(?<!\d)(\d{1,3})\s*/\s*(\d{1,3})\s*(×|x|\*|·|⋅|÷|:)\s*(\d{1,3})\s*/\s*(\d{1,3})(?!\d)")
DECIMAL_RE = re.compile(r"\d+\,\d+|\d+\.\d+")
PERCENT_RE = re.compile(r"\b(\d{1,3})\s*%")

# Palabras de unidades (robusto, sin confundir "l" suelta)
UNIT_PAT = re.compile(
    r"\b(km|m|cm|mm|kg|g|mg|ml|mililitro[s]?|litro[s]?|seg|s|min|h|hora[s]?)\b",
    re.IGNORECASE
)
def is_units_query(text: str) -> bool:
    return bool(UNIT_PAT.search(text))

# ---------- Helpers división (ASCII estilo pizarra) ----------
def precompute_division_steps(n: int, d: int) -> List[Tuple[int,int,int]]:
    s = str(n); steps = []; i = 0
    if int(s[0]) >= d:
        block = int(s[0]); i = 1
    else:
        block = int(s[:2]); i = 2
    while True:
        q = block // d
        r = block - q*d
        steps.append((block, q, r))
        if i >= len(s): break
        block = r*10 + int(s[i]); i += 1
        while block < d and i < len(s):
            steps.append((block, 0, block))
            block = block*10 + int(s[i]); i += 1
    return steps

def ascii_long_division(n: int, d: int, upto: Optional[int] = None) -> str:
    steps = precompute_division_steps(n, d)
    if upto is None: upto = len(steps)
    upto = max(0, min(upto, len(steps)))

    header = f"{d} ⟌ {n}"
    width = max(len(header), 16)
    lines = [header]
    for idx, (block, q, r) in enumerate(steps[:upto]):
        prod = d*q
        lines.append(f"{('- ' + str(prod)).rjust(width)}")
        lines.append(f"{('  ' + str(r)).rjust(width)}")

    if upto == len(steps):
        quotient = int("".join(str(q) for (_,q,_) in steps)) if steps else 0
        remainder = steps[-1][2] if steps else 0
        lines.append("")
        lines.append(f"Cociente: {quotient}    Resto: {remainder}")

    return "\n".join(lines)

def ascii_multiples_table(d: int, steps: List[Tuple[int,int,int]]) -> str:
    ks = set()
    for _, q, _ in steps:
        for k in [q-1, q, q+1]:
            if 0 < k < 10: ks.add(k)
    L = sorted(ks)
    if not L: return ""
    rows = [f"{d} × {k} = {d*k}" for k in L]
    return "\n".join(rows)

def ascii_proof(q: int, d: int, r: int, n: int) -> str:
    w = max(len(str(n)), len(str(q)), len(str(d))) + 2
    u = d % 10
    t = d - u
    p1 = q * u
    p2 = q * t
    lines = []
    lines.append(f"{str(q).rjust(w)}")
    lines.append(f"×{str(d).rjust(w-1)}")
    lines.append("-"*w)
    lines.append(f"{str(p1).rjust(w)}")
    lines.append(f"+{str(p2).rjust(w-1)}")
    lines.append("-"*w)
    lines.append(f"{str(p1+p2).rjust(w)}")
    lines.append(f"+{str(r).rjust(w-1)}")
    lines.append("-"*w)
    lines.append(f"{str(n).rjust(w)}")
    return "\n".join(lines)

# ========== Flujos principales ==========
def flow_add(history, msg, a, b) -> ChatResponse:
    t = (f"1) Suma {a} + {b} por columnas.\n"
         "2) Empieza por unidades; si pasa de 9, escribe la unidad y **lleva** 1.\n"
         "3) ¿Qué te da en la primera columna?")
    return ChatResponse(steps=steps_only(latexify(t)), reply=latexify(t))

def flow_sub(history, msg, a, b) -> ChatResponse:
    t = (f"1) Resta {a} − {b} por columnas.\n"
         "2) Si no puedes, **pide prestado** a la columna de la izquierda (1 decena = 10 unidades).\n"
         "3) ¿Qué haces en la columna de unidades?")
    return ChatResponse(steps=steps_only(latexify(t)), reply=latexify(t))

def flow_mul_single(history, msg, a, d) -> ChatResponse:
    t = (f"1) Multiplica {a} × {d}.\n"
         "2) Columna a columna (lleva si hace falta).\n"
         "3) ¿Cuánto te da en unidades?")
    return ChatResponse(steps=steps_only(latexify(t)), reply=latexify(t))

def flow_mul_multi(history, msg, a, m) -> ChatResponse:
    t = (f"1) Multiplicamos {a} × {m}.\n"
         "2) Calcula los **parciales** por unidades/decenas/centenas del multiplicador y luego **súmalos**.\n"
         "3) Dame el primer parcial (unidades).")
    return ChatResponse(steps=steps_only(latexify(t)), reply=latexify(t))

def flow_mul(history, msg, a, m) -> ChatResponse:
    return flow_mul_single(history, msg, a, m) if m < 10 else flow_mul_multi(history, msg, a, m)

# ---- División interactiva con esquema estilo pizarra ----
def count_div_prompts(history: List[Dict[str,str]]) -> int:
    return sum(1 for t in history or [] if t.get("role")=="assistant" and "⟌" in t.get("content",""))

def flow_div(history: List[Dict[str,str]], msg: str, n: int, d: int) -> ChatResponse:
    steps = precompute_division_steps(n, d)
    done = count_div_prompts(history)  # pasos ya mostrados
    done = min(done, len(steps))

    # Estado actual del dibujo
    ascii_now = ascii_long_division(n, d, upto=done)
    header = f"```txt\n{ascii_now}\n```"

    if done == 0:
        block, qexp, _ = steps[0]
        multiples = ascii_multiples_table(d, steps[:1])
        right = f"\n**Pruebas de múltiplos**:\n```txt\n{multiples}\n```" if multiples else ""
        t = (f"{header}\n"
             f"1) Empezamos por el primer **bloque** {block}. ¿Cuántas veces **cabe** {d} en {block}? "
             f"Escribe el cociente y el resto (tras la resta).{right}")
        t = latexify(t); return ChatResponse(steps=steps_only(t), reply=t)

    # Evaluación del paso anterior
    la = last_turn(history, "assistant")
    lu = last_turn(history, "user") or {"content": msg}
    prev_idx = done-1
    block, qexp, rexp = steps[prev_idx]
    nums = ints(lu["content"])
    ok_q = qexp in nums
    ok_r = rexp in nums

    if not (ok_q and ok_r):
        multiples = ascii_multiples_table(d, steps[max(0,prev_idx-1):prev_idx+2])
        hint = (f"{header}\n"
                f"1) Paso de división {prev_idx+1} de {len(steps)}.\n"
                f"2) Busca el **mayor múltiplo** de {d} que **no supere** {block} y resta.\n"
                f"3) Dime cociente y resto.\n")
        if multiples:
            hint += f"\n**Pruebas de múltiplos**:\n```txt\n{multiples}\n```"
        return ChatResponse(steps=steps_only(latexify(hint)), reply=latexify(hint))

    # Avanzamos
    if done < len(steps):
        ascii_next = ascii_long_division(n, d, upto=done+1)
        block_next = steps[done][0] if done < len(steps) else None
        multiples = ascii_multiples_table(d, steps[max(0,done-1):done+2])
        right = f"\n**Pruebas de múltiplos**:\n```txt\n{multiples}\n```" if multiples else ""
        if block_next is not None:
            t = (f"```txt\n{ascii_next}\n```\n"
                 f"1) Paso de división {done+1} de {len(steps)}.\n"
                 f"2) Baja la siguiente cifra y forma el **bloque** {block_next}.\n"
                 f"3) ¿Cuántas veces **cabe** {d} en {block_next}? Di cociente y resto.{right}")
        else:
            t = f"```txt\n{ascii_next}\n```\n1) Ya no quedan cifras por bajar."
        return ChatResponse(steps=steps_only(latexify(t)), reply=latexify(t))

    # Final con prueba
    quotient = int("".join(str(q) for (_,q,_) in steps))
    remainder = steps[-1][2]
    proof = ascii_proof(quotient, d, remainder, n)
    final = (f"```txt\n{ascii_long_division(n, d, upto=None)}\n```\n"
             f"**Prueba final:**\n```txt\n{proof}\n```\n"
             f"1) Resultado: cociente **{quotient}**, resto **{remainder}**.\n"
             f"2) Comprueba que {quotient} × {d} + {remainder} = {n}. ¿Todo cuadra?")
    return ChatResponse(steps=steps_only(latexify(final)), reply=latexify(final))

# ---------- Decimales / Fracciones / Porcentajes (resumen) ----------
def flow_decimals(history, msg) -> ChatResponse:
    t = ("1) Alinea comas para sumar/restar.\n"
         "2) En multiplicación: multiplica como enteros y coloca la coma según cifras decimales totales.\n"
         "3) En división por 10/100/1000: mueve la coma a la izquierda.")
    return ChatResponse(steps=steps_only(latexify(t)), reply=latexify(t))

def flow_frac(history, msg) -> ChatResponse:
    m2 = FRAC2_RE.search(msg)
    if m2:
        a,b,op,c,dn = int(m2.group(1)), int(m2.group(2)), m2.group(3), int(m2.group(4)), int(m2.group(5))
        t = (f"1) Busca el **MCM** de {b} y {dn}.\n"
             f"2) Pasa a denominador común y opera numeradores.\n"
             f"3) **Simplifica** el resultado.")
        return ChatResponse(steps=steps_only(latexify(t)), reply=latexify(t))
    t = ("1) Dime si quieres **sumar/restar** (MCM), **multiplicar** o **dividir** fracciones y tu ejemplo.")
    return ChatResponse(steps=steps_only(latexify(t)), reply=latexify(t))

def flow_percent(history, msg) -> ChatResponse:
    t = ("1) % ↔ fracción: p/100; % ↔ decimal: mueve 2 posiciones.\n"
         "2) p% de N: p/100 × N.\n"
         "3) “¿Qué % es A de B?”: A/B × 100.")
    return ChatResponse(steps=steps_only(latexify(t)), reply=latexify(t))

# ---------- LLM fallback ----------
SYSTEM_PROMPT = (
    "Eres Tutorín (6.º Primaria). Responde en pasos y termina con UNA pregunta. "
    "Usa LaTeX para fracciones y evita revelar el resultado final si puedes guiar."
)

def llm_reply(history: List[Dict[str,str]], user_message: str, grade: str) -> ChatResponse:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for t in history or []:
        r,c = t.get("role",""), t.get("content","")
        if r in {"user","assistant"} and c: messages.append({"role": r, "content": c})
    messages.append({"role":"user","content":f"Curso: {grade}\nAlumno: {user_message}"} )
    out = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL","gpt-4o-mini"),
        temperature=0.2,
        messages=messages,
    )
    reply = (out.choices[0].message.content or "").strip()
    reply = latexify(reply)
    return ChatResponse(steps=steps_only(reply), reply=reply)

# ---------- Router ----------
def detect_route(txt: str) -> str:
    if DECIMAL_RE.search(txt): return "decimals"
    if FRAC2_RE.search(txt) or FRAC_MUL_DIV_RE.search(txt) or "fracción" in txt.lower() or "fraccion" in txt.lower(): return "frac"
    if PERCENT_RE.search(txt) or "porcent" in txt.lower(): return "percent"
    if is_units_query(txt) or "convert" in txt.lower() or "convierte" in txt.lower(): return "units"  # (si implementas flow_units)
    if ADD_RE.search(txt): return "add"
    if SUB_RE.search(txt): return "sub"
    if MUL_RE.search(txt): return "mul"
    if DIV_RE.search(txt): return "div"
    return "llm"

# ---------- Endpoints ----------
@app.get("/ping")
def ping():
    return {"ok": True, "message": "Tutorín está vivo 👋"}

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(status_code=500, detail="Falta OPENAI_API_KEY en el servidor.")
    user_message = (req.message or req.text or "").strip()
    if not user_message:
        raise HTTPException(status_code=400, detail="El campo 'message'/'text' está vacío.")

    route = detect_route(user_message)
    try:
        if route == "add":
            a,b = map(int, ADD_RE.search(user_message).groups())
            return flow_add(req.history, user_message, a, b)
        if route == "sub":
            a,b = map(int, SUB_RE.search(user_message).groups())
            return flow_sub(req.history, user_message, a, b)
        if route == "mul":
            a,m = map(int, MUL_RE.search(user_message).groups())
            return flow_mul(req.history, user_message, a, m)
        if route == "div":
            n,d = map(int, DIV_RE.search(user_message).groups())
            return flow_div(req.history, user_message, n, d)
        if route == "decimals":
            return flow_decimals(req.history, user_message)
        if route == "frac":
            return flow_frac(req.history, user_message)
        if route == "percent":
            return flow_percent(req.history, user_message)
        return llm_reply(req.history, user_message, req.grade or "Primaria")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT","8000")), reload=True)
