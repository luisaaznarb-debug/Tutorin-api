import os
import re
import base64
from typing import List, Optional, Dict, Tuple

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI

from dotenv import load_dotenv
load_dotenv()

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

# ---------- Utilidades numéricas ----------
def gcd(a: int, b: int) -> int:
    while b:
        a, b = b, a % b
    return abs(a)

def lcm(a: int, b: int) -> int:
    return abs(a * b) // gcd(a, b) if a and b else 0

def ints(s: str) -> List[int]:
    return [int(x) for x in re.findall(r"-?\d+", s or "")]

def any_says_no(text: str) -> bool:
    t = (text or "").lower().strip()
    return "no sé" in t or "no se" in t or t in {"no", "ns", "ni idea", "help", "ayuda"}

# ---------- LaTeX seguro ----------
def latexify(t: str) -> str:
    # 2/3 -> \frac{2}{3}
    t = re.sub(r"(?<!\d)(\d{1,3})\s*/\s*(\d{1,3})(?!\d)", r"$\\frac{\1}{\2}$", t)
    # exponentes
    t = re.sub(r"([A-Za-z])\s*\^\s*(\d+)", r"\1^{\2}", t)
    # multiplicación/división
    t = re.sub(r"(?<!\*)\*(?!\*)", r" $\\times$ ", t)
    t = re.sub(r"\\times", r"$\\times$", t)
    t = t.replace("×", " $\\times$ ").replace("·", " $\\times$ ").replace("⋅", " $\\times$ ")
    t = t.replace("÷", " $\\div$ ").replace(":", " $\\div$ ")
    return t

# ---------- Pequeño motor de SVG (Data URI) ----------
def _svg_data(svg: str) -> str:
    data = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{data}"

def ascii_to_svg_data_uri(block: str, font_size: int = 16) -> str:
    lines = (block or "").splitlines() or [""]
    max_len = max(len(x) for x in lines)
    char_w = 9
    line_h = int(font_size * 1.25)
    pad = 12
    width = pad * 2 + char_w * max_len
    height = pad * 2 + line_h * len(lines)
    text_elems = []
    y = pad + line_h
    for ln in lines:
        text_elems.append(
            f'<text x="{pad}" y="{y}" font-family="ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, \'Liberation Mono\', \'Courier New\', monospace" font-size="{font_size}" fill="#111827">{ln.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")}</text>'
        )
        y += line_h
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"><rect width="100%" height="100%" fill="#fff" stroke="#e5e7eb"/>{"".join(text_elems)}</svg>'
    return _svg_data(svg)

# ---- Barras de fracción (para suma/resta y equivalencias) ----
def svg_bar(n: int, d: int, width: int = 420, height: int = 42, color: str = "#60a5fa", label: str = "") -> str:
    d = max(1, d)
    n = max(0, min(n, d))
    seg_w = width / d
    rects = []
    # fondo
    rects.append(f'<rect x="0" y="0" width="{width}" height="{height}" rx="6" ry="6" fill="#ffffff" stroke="#cbd5e1"/>')
    # segmentos
    for i in range(d):
        fill = color if i < n else "#ffffff"
        rects.append(f'<rect x="{i*seg_w}" y="0" width="{seg_w}" height="{height}" fill="{fill}" stroke="#cbd5e1"/>')
    # etiqueta
    if label:
        rects.append(f'<text x="{width/2}" y="{height+16}" text-anchor="middle" font-size="12" fill="#334155">{label}</text>')
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height+20}">{"".join(rects)}</svg>'
    return _svg_data(svg)

def svg_two_bars(a:int,b:int,c:int,d:int, title:str="") -> str:
    bar1 = svg_bar(a,b,label=f"{a}/{b}")
    bar2 = svg_bar(c,d,color="#f59e0b",label=f"{c}/{d}")
    # montamos dos <img> en un SVG grande (para zoom nítido)
    W, H = 460, 150
    svg = f"""
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}">
  <rect width="100%" height="100%" fill="#fff"/>
  <text x="{W/2}" y="20" text-anchor="middle" font-size="14" fill="#111827">{title}</text>
  <image href="{bar1}" x="20" y="30" height="50"/>
  <image href="{bar2}" x="20" y="90" height="50"/>
</svg>
"""
    return _svg_data(svg)

# ---- Modelo de área (multiplicación de fracciones) ----
def svg_area_mul(a:int,b:int,c:int,d:int) -> str:
    b = max(1, b); d = max(1, d)
    W, H = 420, 260
    pad = 30
    grid_w, grid_h = W - 2*pad, H - 2*pad - 20
    # dimensiones reales
    col_w = grid_w / b
    row_h = grid_h / d
    # colores
    col_color = "#60a5fa"  # azul columnas (a)
    row_color = "#f59e0b"  # naranja filas (c)
    inter_color = "#8b5cf6"  # morado intersección

    rects = []
    # fondo
    rects.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="#fff" stroke="#e5e7eb"/>')
    # marco de la rejilla
    rects.append(f'<rect x="{pad}" y="{pad}" width="{grid_w}" height="{grid_h}" fill="#ffffff" stroke="#0f172a"/>')

    # columnas sombreadas (a)
    shade_w = max(0, min(a, b)) * col_w
    rects.append(f'<rect x="{pad}" y="{pad}" width="{shade_w}" height="{grid_h}" fill="{col_color}" fill-opacity="0.25"/>')

    # filas sombreadas (c)
    shade_h = max(0, min(c, d)) * row_h
    rects.append(f'<rect x="{pad}" y="{pad}" width="{grid_w}" height="{shade_h}" fill="{row_color}" fill-opacity="0.25"/>')

    # intersección a*c
    rects.append(f'<rect x="{pad}" y="{pad}" width="{shade_w}" height="{shade_h}" fill="{inter_color}" fill-opacity="0.35"/>')

    # líneas de rejilla
    for i in range(1, b):
        x = pad + i*col_w
        rects.append(f'<line x1="{x}" y1="{pad}" x2="{x}" y2="{pad+grid_h}" stroke="#cbd5e1"/>')
    for j in range(1, d):
        y = pad + j*row_h
        rects.append(f'<line x1="{pad}" y1="{y}" x2="{pad+grid_w}" y2="{y}" stroke="#cbd5e1"/>')

    # texto
    inter_num = max(0, min(a, b)) * max(0, min(c, d))
    total = b * d
    label = f"{a}/{b} × {c}/{d} = {inter_num}/{total}"
    rects.append(f'<text x="{W/2}" y="{H-6}" text-anchor="middle" font-size="14" fill="#111827">{label}</text>')

    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}">{"".join(rects)}</svg>'
    return _svg_data(svg)

# ---------- Helpers de respuesta ----------
INVIS = "\u2063"
TAG_ADD = f"{INVIS}A{INVIS}"
TAG_SUB = f"{INVIS}S{INVIS}"
TAG_MUL = f"{INVIS}M{INVIS}"
TAG_DIV = f"{INVIS}D{INVIS}"
TAG_FR  = f"{INVIS}F{INVIS}"
TAG_PCT = f"{INVIS}P{INVIS}"

def step(text: str, image: Optional[str] = None) -> ChatResponse:
    text = latexify(text)
    return ChatResponse(steps=[Step(text=text, imageUrl=image)], reply=text)

def count_key(history: List[Dict[str, str]], key: str) -> int:
    return sum(1 for t in history or [] if t.get("role") == "assistant" and key in (t.get("content") or ""))

# ---------- Detecciones ----------
ADD_RE = re.compile(r"\b(\d{1,12})\s*\+\s*(\d{1,12})\b")
SUB_RE = re.compile(r"\b(\d{1,12})\s*-\s*(\d{1,12})\b")
MUL_RE = re.compile(r"\b(\d{1,12})\s*(?:×|x|\*)\s*(\d{1,8})\b")
DIV_RE = re.compile(r"\b(\d{1,12})\s*(?:÷|:|\/)\s*(\d{1,6})\b")

FRAC2_RE = re.compile(r"(?<!\d)(\d{1,3})\s*/\s*(\d{1,3})\s*([+-])\s*(\d{1,3})\s*/\s*(\d{1,3})(?!\d)")
FRAC_MUL_DIV_RE = re.compile(r"(?<!\d)(\d{1,3})\s*/\s*(\d{1,3})\s*(×|x|\*|·|⋅|÷|:)\s*(\d{1,3})\s*/\s*(\d{1,3})(?!\d)")

DECIMAL_RE = re.compile(r"\d+\,\d+|\d+\.\d+")
PERCENT_RE = re.compile(r"\b(\d{1,3})\s*%\s*de\s*(\d{1,12})(?!\S)", re.IGNORECASE)

UNIT_PAT = re.compile(
    r"\b(km|m|cm|mm|kg|g|mg|ml|mililitro[s]?|litro[s]?|seg|s|min|h|hora[s]?)\b",
    re.IGNORECASE,
)
def is_units_query(text: str) -> bool:
    return bool(UNIT_PAT.search(text or ""))

# ---------- ASCII helpers (suma/resta/div/mult) ----------
def precompute_division_steps(n: int, d: int) -> List[Tuple[int, int, int]]:
    s = str(n)
    steps = []
    i = 0
    if int(s[0]) >= d:
        block = int(s[0]); i = 1
    else:
        block = int(s[:2]); i = 2
    while True:
        q = block // d
        r = block - q * d
        steps.append((block, q, r))
        if i >= len(s): break
        block = r * 10 + int(s[i]); i += 1
        while block < d and i < len(s):
            steps.append((block, 0, block))
            block = block * 10 + int(s[i]); i += 1
    return steps

def ascii_long_division(n: int, d: int, upto: Optional[int] = None) -> str:
    steps = precompute_division_steps(n, d)
    if upto is None: upto = len(steps)
    upto = max(0, min(upto, len(steps)))
    header = f"{d} ⟌ {n}"
    width = max(len(header), 16)
    lines = [header]
    for idx, (block, q, r) in enumerate(steps[:upto]):
        prod = d * q
        lines.append(f"{('- ' + str(prod)).rjust(width)}")
        lines.append(f"{('  ' + str(r)).rjust(width)}")
    if upto == len(steps):
        quotient = int("".join(str(q) for (_, q, _) in steps)) if steps else 0
        remainder = steps[-1][2] if steps else 0
        lines.append("")
        lines.append(f"Cociente: {quotient}    Resto: {remainder}")
    return "\n".join(lines)

def ascii_proof_mul_sum(partials: List[int], multiplier: int, multiplicand: int) -> str:
    width = max(len(str(sum(partials))), len(str(multiplier)), len(str(multiplicand))) + 3
    lines = [f"{str(multiplicand).rjust(width)}",
             f"×{str(multiplier).rjust(width-1)}",
             "-" * width]
    for i, p in enumerate(partials):
        lines.append(f"{str(p).rjust(width-i)}")
    lines.append("-" * width)
    lines.append(f"{str(sum(partials)).rjust(width)}")
    return "\n".join(lines)

def ascii_proof_add(a: int, b: int, s: int) -> str:
    width = max(len(str(a)), len(str(b)), len(str(s))) + 2
    return "\n".join([str(a).rjust(width), f"+{str(b).rjust(width-1)}", "-" * width, str(s).rjust(width)])

def ascii_proof_sub(a: int, b: int, r: int) -> str:
    width = max(len(str(a)), len(str(b)), len(str(r))) + 2
    return "\n".join([str(a).rjust(width), f"-{str(b).rjust(width-1)}", "-" * width, str(r).rjust(width)])

# ---------- Suma/resta por columnas (interactivas) ----------
def add_columns(a: int, b: int):
    da = list(map(int, str(a)[::-1]))
    db = list(map(int, str(b)[::-1]))
    L = max(len(da), len(db))
    da += [0] * (L - len(da))
    db += [0] * (L - len(db))
    return da, db, L

def sub_columns(a: int, b: int):
    da = list(map(int, str(a)[::-1]))
    db = list(map(int, str(b)[::-1]))
    L = max(len(da), len(db))
    da += [0] * (L - len(da))
    db += [0] * (L - len(db))
    return da, db, L

def count_add_stage(history: List[Dict[str, str]]) -> int:
    return count_key(history, TAG_ADD)

def count_sub_stage(history: List[Dict[str, str]]) -> int:
    return count_key(history, TAG_SUB)

def count_mul_stage(history: List[Dict[str, str]]) -> int:
    return count_key(history, TAG_MUL)

def count_div_prompts(history: List[Dict[str, str]]) -> int:
    return count_key(history, TAG_DIV)

# ---------- Flujos básicos (add/sub/mul/div enteros) ----------
def flow_add(history, msg, a, b) -> ChatResponse:
    da, db, L = add_columns(a, b)
    stage = count_add_stage(history)
    if stage > 0:
        nums = ints(msg)
        carry = 0
        for i in range(stage):
            s = da[i] + db[i] + carry
            digit = s % 10
            carry = s // 10
        ok = (digit in nums) and (carry in nums)
        if not ok or any_says_no(msg):
            t = (f"{TAG_ADD} Pista: en **columna {stage}** sumaste {da[stage-1]} + {db[stage-1]}"
                 f"{' + 1 (llevas)' if (stage>1 and (da[stage-2]+db[stage-2])>=10) else ''}. "
                 f"Dígito {digit}, llevas {carry}. Vamos a repetir.")
            return step(t)
    if stage < L:
        carry = 0
        for i in range(stage):
            s = da[i] + db[i] + carry
            carry = s // 10
        t = (f"{TAG_ADD} Pista: columna **{stage+1}** → {da[stage]} + {db[stage]}"
             f"{' + 1 (llevas)' if carry else ''}. Di dígito y lo que llevas (0/1).")
        return step(t)
    ans = a + b
    img = ascii_to_svg_data_uri(ascii_proof_add(a, b, ans))
    t = (f"{TAG_ADD} ¡Listo! Resultado: **{ans}**.\n\nPrueba:\n```txt\n{ascii_proof_add(a,b,ans)}\n```")
    return step(t, image=img)

def flow_sub(history, msg, a, b) -> ChatResponse:
    da, db, L = sub_columns(a, b)
    stage = count_sub_stage(history)
    if stage > 0:
        nums = ints(msg)
        borrow = 0
        for i in range(stage):
            x = da[i] - borrow
            need = 1 if x < db[i] else 0
            digit = (x + (10 if need else 0)) - db[i]
            borrow = need
        ok = (digit in nums) and (borrow in nums)
        if not ok or any_says_no(msg):
            t = (f"{TAG_SUB} Pista: en **columna {stage}** si no alcanza, **pide prestado**. "
                 f"Repasa: dígito {digit}, llevas {borrow}. Probemos otra vez.")
            return step(t)
    if stage < L:
        borrow = 0
        for i in range(stage):
            x = da[i] - borrow
            borrow = 1 if x < db[i] else 0
        t = (f"{TAG_SUB} Pista: columna **{stage+1}**: "
             f"{da[stage]} {'(menos 1 por préstamo) ' if borrow else ''}− {db[stage]}. "
             "Di dígito y si pides prestado (0/1).")
        return step(t)
    ans = a - b
    img = ascii_to_svg_data_uri(ascii_proof_sub(a, b, ans))
    t = (f"{TAG_SUB} ¡Hecho! Resultado: **{ans}**.\n\nPrueba:\n```txt\n{ascii_proof_sub(a,b,ans)}\n```")
    return step(t, image=img)

def flow_mul(history, msg, a, m) -> ChatResponse:
    digits = list(map(int, str(m)[::-1]))
    stage = count_mul_stage(history)
    if stage > 0 and stage <= len(digits):
        nums = ints(msg)
        expected = a * digits[stage - 1]
        if not (expected in nums) or any_says_no(msg):
            t = (f"{TAG_MUL} Pista: el **parcial {stage}** es {a} × {digits[stage-1]} = {expected}. "
                 f"Vamos con el siguiente.")
            return step(t)
    if stage < len(digits):
        t = (f"{TAG_MUL} Pista: calcula el **parcial {stage+1}** → {a} × {digits[stage]}. "
             "Escribe solo ese número.")
        return step(t)
    partials = [a * d * (10 ** i) for i, d in enumerate(digits)]
    final = a * m
    proof = ascii_proof_mul_sum([a*d for d in digits], m, a)
    img = ascii_to_svg_data_uri(proof)
    t = (f"{TAG_MUL} Muy bien. Ahora **suma los parciales** → resultado **{final}**.\n\n"
         f"Parciales:\n```txt\n{proof}\n```")
    return step(t, image=img)

def flow_div(history: List[Dict[str, str]], msg: str, n: int, d: int) -> ChatResponse:
    steps = precompute_division_steps(n, d)
    done = count_div_prompts(history)
    done = min(done, len(steps))
    ascii_now = ascii_long_division(n, d, upto=done)
    img = ascii_to_svg_data_uri(ascii_now)
    header = f"```txt\n{ascii_now}\n```"
    if done == 0:
        block, qexp, _ = steps[0]
        t = (f"{TAG_DIV} {header}\n"
             f"Pista 1: bloque {block}. ¿Cuántas veces **cabe** {d} en {block}? "
             f"Di cociente y resto.")
        return step(t, image=img)
    prev_idx = done - 1
    block, qexp, rexp = steps[prev_idx]
    nums = ints(msg)
    if not (qexp in nums and rexp in nums) or any_says_no(msg):
        hint = (f"{TAG_DIV} {header}\n"
                f"Pista: busca el mayor múltiplo de {d} ≤ {block} y resta. "
                f"Di cociente y resto.")
        return step(hint, image=img)
    if done < len(steps):
        ascii_next = ascii_long_division(n, d, upto=done + 1)
        img2 = ascii_to_svg_data_uri(ascii_next)
        block_next = steps[done][0] if done < len(steps) else None
        t = (f"{TAG_DIV} ```txt\n{ascii_next}\n```\n"
             f"Baja la siguiente cifra y forma el bloque {block_next}. "
             f"¿Cuántas veces **cabe** {d}? Di cociente y resto.")
        return step(t, image=img2)
    quotient = int("".join(str(q) for (_, q, _) in steps))
    remainder = steps[-1][2]
    final_ascii = ascii_long_division(n, d, upto=None)
    imgf = ascii_to_svg_data_uri(final_ascii)
    final = (f"{TAG_DIV} ```txt\n{final_ascii}\n```\n"
             f"Resultado: cociente **{quotient}**, resto **{remainder}**. "
             f"Comprueba que {quotient} × {d} + {remainder} = {n}.")
    return step(final, image=imgf)

# ---------- Fracciones: +/− ----------
def extract_frac_addsub(history: List[Dict[str, str]], msg: str):
    all_msgs = (history or []) + [{"role": "user", "content": msg}]
    for t in reversed(all_msgs):
        m = FRAC2_RE.search(t.get("content", ""))
        if m:
            a, b, op, c, dn = int(m.group(1)), int(m.group(2)), m.group(3), int(m.group(4)), int(m.group(5))
            return a, b, op, c, dn
    return None

def frac_stage(history: List[Dict[str, str]]) -> str:
    last_assistant = ""
    for t in reversed(history or []):
        if t.get("role") == "assistant":
            last_assistant = t.get("content") or ""
            break
    c = last_assistant.lower()
    if "mcm" in c and "¿cuál es" in c: return "mcm"
    if "¿qué numeradores" in c or "dime dos numeradores" in c: return "nums"
    if "¿cuánto da la suma" in c or "¿cuánto da la resta" in c: return "sum"
    if "simplifica" in c: return "simp"
    return "init"

def flow_frac_addsub(history: List[Dict[str, str]], msg: str) -> ChatResponse:
    prob = extract_frac_addsub(history, msg)
    if not prob:
        return step(f"{TAG_FR} Dime una operación con fracciones, por ejemplo: 2/3 + 5/7 o 4/5 - 1/10.")
    a, b, op, c, dn = prob
    verb = "suma" if op == "+" else "resta"
    st = frac_stage(history)

    # Pista 1
    if st == "init":
        if b == dn:
            img = svg_two_bars(a, b, c, dn, title=f"Barras con denominador común {b}")
            t = (f"{TAG_FR} Pista 1: ya tienen el mismo denominador ({b}). "
                 f"{verb.capitalize()} **los numeradores** y mantén {b}. "
                 f"¿Cuál es el numerador resultante?")
            return step(t, image=img)
        else:
            img = svg_two_bars(a, b, c, dn, title="Observa que los denominadores son distintos")
            return step(f"{TAG_FR} Pista 1: busca el **MCM** de {b} y {dn}. ¿Cuál es el MCM?", image=img)

    if st == "mcm":
        nums = ints(msg)
        L = lcm(b, dn)
        ok = L in nums and L != 0
        if not ok or any_says_no(msg):
            t = (f"{TAG_FR} Pista: lista múltiplos de {b} y de {dn} y elige el primero común. "
                 f"Escribe el MCM.")
            return step(t)
        n1, n2 = a*(L//b), c*(L//dn)
        # barras convertidas
        img = svg_two_bars(n1, L, n2, L, title=f"Equivalencias con denominador {L}")
        return step(f"{TAG_FR} ¡Bien! Pista 2: convierte a denominador {L}. "
                    f"¿Qué **numeradores** quedan? (dime dos)", image=img)

    if st == "nums":
        L = lcm(b, dn); n1 = a*(L//b); n2 = c*(L//dn)
        nums2 = ints(msg)
        if not ((n1 in nums2) and (n2 in nums2)) or any_says_no(msg):
            img = svg_two_bars(n1, L, n2, L, title=f"Equivalencias: {a}/{b}→{n1}/{L} y {c}/{dn}→{n2}/{L}")
            return step(f"{TAG_FR} Pista: los numeradores son {n1} y {n2}. Escríbelos.", image=img)
        op_sym = "+" if op == "+" else "−"
        return step(f"{TAG_FR} ¡Perfecto! Ahora {verb} {n1} {op_sym} {n2} y deja {L}. "
                    f"¿Cuánto da la {'suma' if op=='+' else 'resta'}?")

    if st == "sum":
        L = lcm(b, dn); n1 = a*(L//b); n2 = c*(L//dn)
        res = n1 + n2 if op == "+" else n1 - n2
        nums3 = ints(msg)
        if not (res in nums3) or any_says_no(msg):
            t = f"{TAG_FR} Pista: {n1} {'+' if op=='+' else '−'} {n2} = {res}. Escribe {res}."
            return step(t)
        g = gcd(abs(res), L)
        if g > 1:
            img = ascii_to_svg_data_uri(f"Simplificar: {res}/{L} ÷ {g} = {res//g}/{L//g}")
            return step(f"{TAG_FR} Pista 4: **simplifica** {res}/{L} dividiendo por {g}. "
                        f"¿Resultado final?", image=img)
        else:
            return step(f"{TAG_FR} ¡Resultado! {res}/{L} ya está simplificada. ¿Otra?")

    if st == "simp":
        L = lcm(b, dn); n1 = a*(L//b); n2 = c*(L//dn)
        res = n1 + n2 if op == "+" else n1 - n2
        g = gcd(abs(res), L); fn = res//g if g else res; fd = L//g if g else L
        nums4 = ints(msg)
        if not ((fn in nums4) and (fd in nums4)) or any_says_no(msg):
            return step(f"{TAG_FR} Pista: {res}/{L} ÷ {g} = {fn}/{fd}. Ese es el resultado.")
        return step(f"{TAG_FR} ¡Genial! Resultado: {fn}/{fd}. ¿Practicamos otra?")

    return step(f"{TAG_FR} Seguimos paso a paso. ¿Qué te gustaría hacer ahora?")

# ---------- Fracciones: × y ÷ con modelos de área ----------
def extract_frac_muldiv(msg: str):
    m = FRAC_MUL_DIV_RE.search(msg or "")
    if not m:
        return None
    a, b, op, c, d = int(m.group(1)), int(m.group(2)), m.group(3), int(m.group(4)), int(m.group(5))
    return a, b, op, c, d

def stage_muldiv(history: List[Dict[str, str]]) -> str:
    last = ""
    for t in reversed(history or []):
        if t.get("role") == "assistant":
            last = (t.get("content") or "").lower()
            break
    if "recíproco" in last or "reciproco" in last: return "reciproco"
    if "¿cuántos cuadritos" in last or "cuantos cuadritos" in last: return "contar"
    if "simplifica" in last: return "simp"
    return "init"

def flow_frac_muldiv(history: List[Dict[str, str]], msg: str) -> ChatResponse:
    prob = extract_frac_muldiv(msg)
    if not prob:
        return step(f"{TAG_FR} Dime algo como 2/3 × 3/5 o 4/7 ÷ 2/3.")
    a, b, op, c, d = prob
    st = stage_muldiv(history)

    # División → convertir a multiplicación por el recíproco
    if op in ("÷", ":"):
        if st == "init":
            guide = f"{a}/{b} ÷ {c}/{d} = {a}/{b} × {d}/{c}"
            img = ascii_to_svg_data_uri(guide)
            return step(f"{TAG_FR} Para dividir fracciones, usa el **recíproco**: "
                        f"{latexify(guide)}. ¿Cuál es el recíproco de {c}/{d}?", image=img)
        # Si ya reconocimos el recíproco, tratamos como multiplicación
        op = "×"
        a2, b2, c2, d2 = a, b, d, c
        return flow_frac_mul(history, msg, a2, b2, c2, d2)

    # Multiplicación directa
    return flow_frac_mul(history, msg, a, b, c, d)

def flow_frac_mul(history: List[Dict[str, str]], msg: str, a:int, b:int, c:int, d:int) -> ChatResponse:
    st = stage_muldiv(history)

    if st == "init":
        img = svg_area_mul(a,b,c,d)
        t = (f"{TAG_FR} Observa el **modelo de área**: sombreamos {a} de {b} columnas (azul) y "
             f"{c} de {d} filas (naranja). "
             f"La **intersección** son los cuadritos morados.\n"
             f"¿Cuántos cuadritos hay en la intersección? ¿Y cuántos en total?")
        return step(t, image=img)

    if st == "contar":
        nums = ints(msg)
        inter = a*c
        total = b*d
        ok = (inter in nums) and (total in nums)
        if not ok or any_says_no(msg):
            img = svg_area_mul(a,b,c,d)
            return step(f"{TAG_FR} Pista: intersección = {a}×{c}={inter}; total = {b}×{d}={total}. "
                        f"Escribe **{inter}** y **{total}**.", image=img)
        g = gcd(inter, total)
        if g > 1:
            simp = f"Simplificar: {inter}/{total} ÷ {g} = {inter//g}/{total//g}"
            img = ascii_to_svg_data_uri(simp)
            return step(f"{TAG_FR} ¡Bien! Producto: {inter}/{total}. "
                        f"Ahora **simplifica** dividiendo por {g}. ¿Resultado final?", image=img)
        else:
            return step(f"{TAG_FR} Resultado: {inter}/{total} ya está simplificado. ¿Otro?")

    if st == "reciproco":
        # ya se explicó, volvemos a modelo de área con d/c
        return flow_frac_mul(history, msg, a, b, c, d)

    if st == "simp":
        inter = a*c
        total = b*d
        g = gcd(inter, total)
        fn = inter//g if g else inter
        fd = total//g if g else total
        nums = ints(msg)
        if not ((fn in nums) and (fd in nums)) or any_says_no(msg):
            return step(f"{TAG_FR} Pista: {inter}/{total} ÷ {g} = {fn}/{fd}. Ese es el resultado.")
        return step(f"{TAG_FR} ¡Genial! {fn}/{fd}. ¿Practicamos otra?")

    # fallback
    img = svg_area_mul(a,b,c,d)
    return step(f"{TAG_FR} Sigamos con el modelo de área. ¿Cuántos cuadritos morados y cuántos en total?", image=img)

# ---------- Porcentajes / Decimales / LLM ----------
def count_pct_stage(history: List[Dict[str, str]]) -> int:
    return count_key(history, TAG_PCT)

def flow_percent(history, msg) -> ChatResponse:
    m = PERCENT_RE.search(msg)
    if not m:
        return step(f"{TAG_PCT} Dime algo como **25% de 200** y lo resolvemos paso a paso.")
    p = int(m.group(1)); N = int(m.group(2))
    stage = count_pct_stage(history)
    if stage == 0:
        return step(f"{TAG_PCT} Pista 1: primero calcula **{p} × {N}**. Escribe ese número.")
    if stage == 1:
        nums = ints(msg)
        expected = p * N
        if not (expected in nums) or any_says_no(msg):
            return step(f"{TAG_PCT} Pista: {p} × {N} = {expected}. Escríbelo para seguir.")
        return step(f"{TAG_PCT} Pista 2: ahora **divide por 100**. ¿Resultado?")
    nums = ints(msg)
    raw = (p * N) / 100
    final_int = int(raw) if raw.is_integer() else None
    ok = (final_int is not None and (final_int in nums)) or (final_int is None and str(raw) in msg)
    if not ok or any_says_no(msg):
        return step(f"{TAG_PCT} Resultado: **{raw}**. ¿Quieres probar otro porcentaje?")
    return step(f"{TAG_PCT} ¡Bien! {p}% de {N} = **{raw}**. ¿Otro?")

def flow_decimals(history, msg) -> ChatResponse:
    return step("Pista: al **sumar/restar decimales**, alinea las **comas**. "
                "En multiplicación, multiplica como enteros y coloca la coma según cifras decimales totales. "
                "Si me das un ejemplo concreto, te guío paso a paso.")

SYSTEM_PROMPT = (
    "Eres Tutorín. Trabajas con **una sola pista** por turno y terminas con **una pregunta**. "
    "Tu objetivo es que el alumno encuentre la solución por sí mismo. "
    "Si falla o dice 'no lo sé', das otra pista más concreta. "
    "Cuando sea adecuado, validas y cierras con una explicación breve. "
    "Usa español de España y LaTeX para fórmulas."
)

def llm_reply(history: List[Dict[str, str]], user_message: str, grade: str) -> ChatResponse:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for t in history or []:
        r, c = t.get("role", ""), t.get("content", "")
        if r in {"user", "assistant"} and c:
            messages.append({"role": r, "content": c})
    messages.append({"role": "user", "content": f"Curso: {grade}\nAlumno: {user_message}"})
    out = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=0.2,
        messages=messages,
    )
    reply = (out.choices[0].message.content or "").strip()
    return step(reply)

# ---------- Router ----------
def detect_route(txt: str) -> str:
    if DECIMAL_RE.search(txt or ""): return "decimals"
    low = (txt or "").lower()
    if FRAC_MUL_DIV_RE.search(txt or ""): return "frac-md"
    if FRAC2_RE.search(txt or "") or "fracción" in low or "fraccion" in low:
        return "frac"
    if PERCENT_RE.search(txt or "") or "porcent" in low: return "percent"
    if is_units_query(txt) or "convert" in low or "convierte" in low: return "units"
    if ADD_RE.search(txt or ""): return "add"
    if SUB_RE.search(txt or ""): return "sub"
    if MUL_RE.search(txt or ""): return "mul"
    if DIV_RE.search(txt or ""): return "div"
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
            a, b = map(int, ADD_RE.search(user_message).groups())
            return flow_add(req.history, user_message, a, b)
        if route == "sub":
            a, b = map(int, SUB_RE.search(user_message).groups())
            return flow_sub(req.history, user_message, a, b)
        if route == "mul":
            a, m = map(int, MUL_RE.search(user_message).groups())
            return flow_mul(req.history, user_message, a, m)
        if route == "div":
            n, d = map(int, DIV_RE.search(user_message).groups())
            return flow_div(req.history, user_message, n, d)
        if route == "decimals":
            return flow_decimals(req.history, user_message)
        if route == "frac":
            return flow_frac_addsub(req.history, user_message)
        if route == "frac-md":
            return flow_frac_muldiv(req.history, user_message)
        if route == "percent":
            return flow_percent(req.history, user_message)
        return llm_reply(req.history, user_message, req.grade or "Primaria")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")), reload=True)
