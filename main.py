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
    while b:
        a, b = b, a % b
    return abs(a)

def lcm(a: int, b: int) -> int:
    return abs(a * b) // gcd(a, b) if a and b else 0

def ints(s: str) -> List[int]:
    return [int(x) for x in re.findall(r"-?\d+", s)]

def last_turn(history: List[Dict[str, str]], role: str) -> Optional[Dict[str, str]]:
    for t in reversed(history or []):
        if t.get("role") == role and t.get("content"):
            return t
    return None

def any_says_no(text: str) -> bool:
    t = (text or "").lower().strip()
    return "no sé" in t or "no se" in t or t in {"no", "ns", "ni idea", "help", "ayuda"}

# LaTeX seguro: no rompe **negritas**, fuerza ×/÷ en modo matemático
def latexify(t: str) -> str:
    # Fracciones simples "a/b" (no URLs)
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

def step(text: str) -> ChatResponse:
    text = latexify(text)
    return ChatResponse(steps=[Step(text=text)], reply=text)

# ---------- Detecciones ----------
ADD_RE = re.compile(r"\b(\d{1,12})\s*\+\s*(\d{1,12})\b")
SUB_RE = re.compile(r"\b(\d{1,12})\s*-\s*(\d{1,12})\b")
MUL_RE = re.compile(r"\b(\d{1,12})\s*(?:×|x|\*)\s*(\d{1,8})\b")
DIV_RE = re.compile(r"\b(\d{1,12})\s*(?:÷|:|\/)\s*(\d{1,6})\b")
FRAC2_RE = re.compile(r"(?<!\d)(\d{1,3})\s*/\s*(\d{1,3})\s*([+-])\s*(\d{1,3})\s*/\s*(\d{1,3})(?!\d)")
FRAC_MUL_DIV_RE = re.compile(r"(?<!\d)(\d{1,3})\s*/\s*(\d{1,3})\s*(×|x|\*|·|⋅|÷|:)\s*(\d{1,3})\s*/\s*(\d{1,3})(?!\d)")
DECIMAL_RE = re.compile(r"\d+\,\d+|\d+\.\d+")
PERCENT_RE = re.compile(r"\b(\d{1,3})\s*%\s*de\s*(\d{1,12})(?!\S)", re.IGNORECASE)

# Palabras de unidades (robusto, sin confundir "l" suelta)
UNIT_PAT = re.compile(
    r"\b(km|m|cm|mm|kg|g|mg|ml|mililitro[s]?|litro[s]?|seg|s|min|h|hora[s]?)\b",
    re.IGNORECASE,
)
def is_units_query(text: str) -> bool:
    return bool(UNIT_PAT.search(text or ""))

# ---------- Etiquetas / contadores por historia ----------
def count_key(history: List[Dict[str, str]], key: str) -> int:
    return sum(1 for t in history or [] if t.get("role") == "assistant" and key in (t.get("content") or ""))

# ---------- Etiquetas de etapas (visibles pero breves) ----------
TAG_ADD = "⟦ADD⟧"
TAG_SUB = "⟦SUB⟧"
TAG_MUL = "⟦MUL⟧"
TAG_DIV = "⟦DIV⟧"
TAG_FR  = "⟦FRAC⟧"
TAG_PCT = "⟦PCT⟧"

# ---------- Place names ----------
PLACE = ["unidades", "decenas", "centenas", "millares",
         "decenas de millar", "centenas de millar",
         "millones", "decenas de millón", "centenas de millón", "miles de millón"]

def place_name(i: int) -> str:
    return PLACE[i] if i < len(PLACE) else f"columna {i+1}"

# ---------- ASCII helpers (div & proofs) ----------
def precompute_division_steps(n: int, d: int) -> List[Tuple[int, int, int]]:
    s = str(n)
    steps = []
    i = 0
    if int(s[0]) >= d:
        block = int(s[0])
        i = 1
    else:
        block = int(s[:2])
        i = 2
    while True:
        q = block // d
        r = block - q * d
        steps.append((block, q, r))
        if i >= len(s):
            break
        block = r * 10 + int(s[i])
        i += 1
        while block < d and i < len(s):
            steps.append((block, 0, block))
            block = block * 10 + int(s[i])
            i += 1
    return steps

def ascii_long_division(n: int, d: int, upto: Optional[int] = None) -> str:
    steps = precompute_division_steps(n, d)
    if upto is None:
        upto = len(steps)
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

def ascii_multiples_table(d: int, steps: List[Tuple[int, int, int]]) -> str:
    ks = set()
    for _, q, _ in steps:
        for k in [q - 1, q, q + 1]:
            if 0 < k < 10:
                ks.add(k)
    L = sorted(ks)
    if not L:
        return ""
    rows = [f"{d} × {k} = {d*k}" for k in L]
    return "\n".join(rows)

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

# ---------- Suma (interactiva por columnas) ----------
def add_columns(a: int, b: int):
    da = list(map(int, str(a)[::-1]))
    db = list(map(int, str(b)[::-1]))
    L = max(len(da), len(db))
    da += [0] * (L - len(da))
    db += [0] * (L - len(db))
    return da, db, L

def count_add_stage(history: List[Dict[str, str]]) -> int:
    return count_key(history, TAG_ADD)

def flow_add(history, msg, a, b) -> ChatResponse:
    da, db, L = add_columns(a, b)
    stage = count_add_stage(history)

    # validar respuesta del paso anterior (stage-1)
    if stage > 0:
        lu = last_turn(history, "user") or {"content": msg}
        nums = ints(lu["content"])
        carry = 0
        ok = True
        for i in range(stage):
            s = da[i] + db[i] + carry
            digit = s % 10
            carry = s // 10
        # En el paso anterior debían haber dicho [digit, carry]
        ok = (digit in nums) and (carry in nums)
        if not ok or any_says_no(lu["content"]):
            t = (f"{TAG_ADD} Pista: en **{place_name(stage-1)}** sumaste {da[stage-1]} + {db[stage-1]}"
                 f"{' + 1 (llevas)' if (stage>1 and (da[stage-2]+db[stage-2])>=10) else ''}. "
                 f"El dígito debe ser {digit} y llevas {carry}. Prueba otra vez. "
                 f"Ahora dime el dígito y lo que llevas para **{place_name(stage)}**: "
                 f"{da[stage]} + {db[stage]}{' + 1' if carry else ''}.")
            return step(t)

    # Si aún quedan columnas → nueva pista para la siguiente columna
    if stage < L:
        carry = 0
        for i in range(stage):
            s = da[i] + db[i] + carry
            carry = s // 10
        t = (f"{TAG_ADD} Pista: **{place_name(stage)}** → {da[stage]} + {db[stage]}"
             f"{' + 1 (llevas)' if carry else ''}. "
             "Dime **dos números**: el dígito que escribes y lo que llevas (0 o 1).")
        return step(t)

    # Paso final: posible carry extra
    carry = 0
    for i in range(L):
        s = da[i] + db[i] + carry
        carry = s // 10
    ans = a + b
    if carry:
        t = (f"{TAG_ADD} Último detalle: ¿hay un **acarreo final**? Sí, {carry}. "
             f"Resultado: **{ans}**.\n\nPrueba:\n```txt\n{ascii_proof_add(a,b,ans)}\n```")
    else:
        t = (f"{TAG_ADD} ¡Listo! Resultado: **{ans}**.\n\nPrueba:\n```txt\n{ascii_proof_add(a,b,ans)}\n```")
    return step(t)

# ---------- Resta (interactiva con préstamo) ----------
def sub_columns(a: int, b: int):
    da = list(map(int, str(a)[::-1]))
    db = list(map(int, str(b)[::-1]))
    L = max(len(da), len(db))
    da += [0] * (L - len(da))
    db += [0] * (L - len(db))
    return da, db, L

def count_sub_stage(history: List[Dict[str, str]]) -> int:
    return count_key(history, TAG_SUB)

def flow_sub(history, msg, a, b) -> ChatResponse:
    da, db, L = sub_columns(a, b)
    stage = count_sub_stage(history)

    # validar paso anterior
    if stage > 0:
        lu = last_turn(history, "user") or {"content": msg}
        nums = ints(lu["content"])
        borrow = 0
        for i in range(stage):
            x = da[i] - borrow
            need = 1 if x < db[i] else 0
            digit = (x + (10 if need else 0)) - db[i]
            borrow = need
        ok = (digit in nums) and (borrow in nums)
        if not ok or any_says_no(lu["content"]):
            t = (f"{TAG_SUB} Pista: en **{place_name(stage-1)}** si no te alcanzaba, "
                 f"**pide prestado**: 1 decena = 10 unidades. "
                 f"Repasa: {da[stage-1]} {'(menos 1 por el préstamo) ' if stage>1 else ''}- {db[stage-1]} → "
                 f"dígito {digit}, llevas {borrow}. Ahora dime dígito y lo que **pides prestado** "
                 f"para **{place_name(stage)}**.")
            return step(t)

    if stage < L:
        # calcula si llega con el posible préstamo acumulado
        borrow = 0
        for i in range(stage):
            x = da[i] - borrow
            borrow = 1 if x < db[i] else 0
        t = (f"{TAG_SUB} Pista: **{place_name(stage)}**: "
             f"{da[stage]} {'(menos 1 por préstamo) ' if borrow else ''}− {db[stage]}. "
             "Dime **dos números**: el dígito que escribes y si pides prestado (0 o 1).")
        return step(t)

    ans = a - b
    t = (f"{TAG_SUB} ¡Hecho! Resultado: **{ans}**.\n\nPrueba:\n```txt\n{ascii_proof_sub(a,b,ans)}\n```")
    return step(t)

# ---------- Multiplicación (interactiva por parciales) ----------
def count_mul_stage(history: List[Dict[str, str]]) -> int:
    return count_key(history, TAG_MUL)

def flow_mul(history, msg, a, m) -> ChatResponse:
    # Descomponemos el multiplicador en dígitos (de unidades a mayores)
    digits = list(map(int, str(m)[::-1]))
    stage = count_mul_stage(history)

    # validar el parcial previo
    if stage > 0 and stage <= len(digits):
        lu = last_turn(history, "user") or {"content": msg}
        nums = ints(lu["content"])
        expected = a * digits[stage - 1]
        ok = expected in nums
        if not ok or any_says_no(lu["content"]):
            t = (f"{TAG_MUL} Pista: el **parcial {stage}** es {a} × {digits[stage-1]} = {expected}. "
                 f"Ahora vamos con el siguiente.")
            return step(t)

    # pedir siguiente parcial
    if stage < len(digits):
        t = (f"{TAG_MUL} Pista: calcula el **parcial {stage+1}** → {a} × {digits[stage]}. "
             "Escribe solo ese número.")
        return step(t)

    # suma de parciales (resultado final)
    partials = [a * d * (10 ** i) for i, d in enumerate(digits)]
    final = a * m
    proof = ascii_proof_mul_sum([a*d for d in digits], m, a)
    t = (f"{TAG_MUL} Muy bien. Ahora **suma los parciales** (recuerda desplazar por 10, 100…): "
         f"{' + '.join(str(a*d*(10**i)) for i,d in enumerate(digits))}. "
         f"Resultado esperado: **{final}**.\n\nParciales (sin desplazamiento):\n```txt\n{proof}\n```")
    return step(t)

# ---------- División (interactiva estilo pizarra) ----------
def count_div_prompts(history: List[Dict[str, str]]) -> int:
    return count_key(history, TAG_DIV)

def flow_div(history: List[Dict[str, str]], msg: str, n: int, d: int) -> ChatResponse:
    steps = precompute_division_steps(n, d)
    done = count_div_prompts(history)
    done = min(done, len(steps))

    ascii_now = ascii_long_division(n, d, upto=done)
    header = f"```txt\n{ascii_now}\n```"

    if done == 0:
        block, qexp, _ = steps[0]
        multiples = ascii_multiples_table(d, steps[:1])
        right = f"\n**Pruebas de múltiplos**:\n```txt\n{multiples}\n```" if multiples else ""
        t = (f"{TAG_DIV} {header}\n"
             f"Pista 1: primer **bloque** {block}. ¿Cuántas veces **cabe** {d} en {block}? "
             f"Escribe el cociente y el resto.{right}")
        return step(t)

    la = last_turn(history, "assistant")
    lu = last_turn(history, "user") or {"content": msg}
    prev_idx = done - 1
    block, qexp, rexp = steps[prev_idx]
    nums = ints(lu["content"])
    ok_q = qexp in nums
    ok_r = rexp in nums

    if not (ok_q and ok_r) or any_says_no(lu["content"]):
        multiples = ascii_multiples_table(d, steps[max(0, prev_idx - 1):prev_idx + 2])
        hint = (f"{TAG_DIV} {header}\n"
                f"Pista: busca el **mayor múltiplo** de {d} que **no supere** {block} y resta. "
                f"Di cociente y resto.")
        if multiples:
            hint += f"\n**Pruebas de múltiplos**:\n```txt\n{multiples}\n```"
        return step(hint)

    if done < len(steps):
        ascii_next = ascii_long_division(n, d, upto=done + 1)
        block_next = steps[done][0] if done < len(steps) else None
        multiples = ascii_multiples_table(d, steps[max(0, done - 1):done + 2])
        right = f"\n**Pruebas de múltiplos**:\n```txt\n{multiples}\n```" if multiples else ""
        if block_next is not None:
            t = (f"{TAG_DIV} ```txt\n{ascii_next}\n```\n"
                 f"Pista: baja la siguiente cifra y forma el **bloque** {block_next}. "
                 f"¿Cuántas veces **cabe** {d} en {block_next}? Di cociente y resto.{right}")
        else:
            t = f"{TAG_DIV} ```txt\n{ascii_next}\n```\n¡Bien! Ya no quedan cifras por bajar."
        return step(t)

    quotient = int("".join(str(q) for (_, q, _) in steps))
    remainder = steps[-1][2]
    proof = (
        f"{str(quotient).rjust(8)}\n"
        f"×{str(d).rjust(7)}\n"
        f"{'-'*8}\n"
        f"{str(quotient*d).rjust(8)}\n"
        f"+{str(remainder).rjust(7)}\n"
        f"{'-'*8}\n"
        f"{str(n).rjust(8)}"
    )
    final = (f"{TAG_DIV} ```txt\n{ascii_long_division(n, d, upto=None)}\n```\n"
             f"**Prueba final:**\n```txt\n{proof}\n```\n"
             f"Resultado: cociente **{quotient}**, resto **{remainder}**. "
             f"Comprueba que {quotient} × {d} + {remainder} = {n}.")
    return step(final)

# ---------- Fracciones 100% interactivas ----------
def extract_frac_problem(history: List[Dict[str, str]], msg: str):
    all_msgs = (history or []) + [{"role": "user", "content": msg}]
    for t in reversed(all_msgs):
        m = FRAC2_RE.search(t.get("content", ""))
        if m:
            a, b, op, c, dn = int(m.group(1)), int(m.group(2)), m.group(3), int(m.group(4)), int(m.group(5))
            return a, b, op, c, dn
    return None

def frac_stage(history: List[Dict[str, str]]) -> str:
    la = last_turn(history, "assistant")
    if not la: return "init"
    c = la["content"].lower()
    if "mcm" in c and "¿cuál es" in c: return "mcm"
    if "qué numeradores" in c: return "nums"
    if "¿cuánto da la suma" in c or "¿cuánto da la resta" in c: return "sum"
    if "¿puedes simplificar" in c or "simplifica" in c: return "simp"
    return "init"

def flow_frac(history: List[Dict[str, str]], msg: str) -> ChatResponse:
    prob = extract_frac_problem(history, msg)
    if not prob:
        return step(f"{TAG_FR} Dime una operación con fracciones, por ejemplo: 2/3 + 5/7 o 4/5 - 1/10.")

    a, b, op, c, dn = prob
    stage = frac_stage(history)

    if stage == "init":
        if b == dn:
            verb = "suma" if op == "+" else "resta"
            t = (f"{TAG_FR} Pista 1: ya tienen el mismo denominador ({b}). "
                 f"{verb.capitalize()} **los numeradores** y mantén el denominador {b}. "
                 f"¿Cuál es el numerador resultante?")
            return step(t)
        else:
            return step(f"{TAG_FR} Pista 1: busca el **MCM** de {b} y {dn}. ¿Cuál es el MCM?")

    if stage == "mcm":
        lu = last_turn(history, "user") or {"content": msg}
        L = lcm(b, dn)
        nums = ints(lu["content"])
        ok = L in nums and L != 0
        if not ok or any_says_no(lu["content"]):
            mult_b = [b*i for i in range(1, 11)]
            mult_d = [dn*i for i in range(1, 11)]
            t = (f"{TAG_FR} Pista: múltiplos de {b}: {mult_b}. Múltiplos de {dn}: {mult_d}. "
                 f"El **MCM** es el primero que sale en ambas listas. ¿Cuál es?")
            return step(t)
        k1 = L // b; k2 = L // dn
        return step(f"{TAG_FR} ¡Bien! El MCM es {L}. Pista 2: convierte a denominador {L}. "
                    f"{a}/{b}×{k1}/{k1} y {c}/{dn}×{k2}/{k2}. "
                    f"¿Qué **numeradores** quedan? (dime dos)")

    if stage == "nums":
        lu = last_turn(history, "user") or {"content": msg}
        L = lcm(b, dn); n1 = a*(L//b); n2 = c*(L//dn)
        nums = ints(lu["content"])
        if not ((n1 in nums) and (n2 in nums)) or any_says_no(lu["content"]):
            return step(f"{TAG_FR} Pista: {a}/{b}→{n1}/{L} y {c}/{dn}→{n2}/{L}. Dime los dos numeradores.")
        verb = "suma" if op == "+" else "resta"
        return step(f"{TAG_FR} ¡Perfecto! Ahora {verb} {n1} {'+' if op=='+' else '−'} {n2} y deja {L}. "
                    f"¿Cuánto da la {'suma' if op=='+' else 'resta'}?")

    if stage == "sum":
        lu = last_turn(history, "user") or {"content": msg}
        L = lcm(b, dn); n1 = a*(L//b); n2 = c*(L//dn)
        res = n1 + n2 if op == "+" else n1 - n2
        nums = ints(lu["content"])
        if not (res in nums) or any_says_no(lu["content"]):
            return step(f"{TAG_FR} Pista: {n1} {'+' if op=='+' else '−'} {n2} = {res}. "
                        f"La fracción es {res}/{L}. Escríbela.")
        g = gcd(abs(res), L)
        if g > 1:
            return step(f"{TAG_FR} Pista 4: **simplifica** {res}/{L} dividiendo por {g}. "
                        f"¿Resultado final?")
        else:
            return step(f"{TAG_FR} ¡Resultado! {res}/{L} ya está simplificada. ¿Otra?")

    if stage == "simp":
        lu = last_turn(history, "user") or {"content": msg}
        L = lcm(b, dn); n1 = a*(L//b); n2 = c*(L//dn)
        res = n1 + n2 if op == "+" else n1 - n2
        g = gcd(abs(res), L); fn = res//g if g else res; fd = L//g if g else L
        nums = ints(lu["content"])
        if not ((fn in nums) and (fd in nums)) or any_says_no(lu["content"]):
            return step(f"{TAG_FR} Pista: {res}/{L} ÷ {g} = {fn}/{fd}. Ese es el resultado.")
        return step(f"{TAG_FR} ¡Genial! Resultado: {fn}/{fd}. ¿Practicamos otra?")

    return step(f"{TAG_FR} Continuemos paso a paso. ¿Qué te gustaría hacer ahora?")

# ---------- Porcentajes (interactivo) ----------
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
        lu = last_turn(history, "user") or {"content": msg}
        nums = ints(lu["content"])
        expected = p * N
        if not (expected in nums) or any_says_no(lu["content"]):
            return step(f"{TAG_PCT} Pista: {p} × {N} = {expected}. Escríbelo para seguir.")
        return step(f"{TAG_PCT} Pista 2: ahora **divide por 100**. ¿Resultado?")

    # stage >=2 → validar final
    lu = last_turn(history, "user") or {"content": msg}
    nums = ints(lu["content"])
    final = (p * N) // 100 if (p * N) % 100 == 0 else (p * N) / 100
    ok = (isinstance(final, int) and (final in nums)) or (not isinstance(final, int) and str(final) in lu["content"])
    if not ok or any_says_no(lu["content"]):
        return step(f"{TAG_PCT} Resultado: **{final}**. ¿Quieres probar otro porcentaje?")
    return step(f"{TAG_PCT} ¡Bien! {p}% de {N} = **{final}**. ¿Otro?")

# ---------- Decimales (pista interactiva ligera) ----------
def flow_decimals(history, msg) -> ChatResponse:
    # Damos pista inicial (validación completa de casos decimales sería extensa).
    return step("Pista: al **sumar/restar decimales**, alinea las **comas**. "
                "En multiplicación, multiplica como enteros y coloca la coma al final según cifras decimales totales. "
                "Si me das un ejemplo concreto, te voy guiando paso a paso.")

# ---------- LLM fallback (otras asignaturas) ----------
SYSTEM_PROMPT = (
    "Eres Tutorín. SIEMPRE trabajas con **una sola pista** por turno y terminas con **una pregunta**. "
    "Objetivo: que el alumno encuentre la solución por sí mismo. "
    "Si falla o dice 'no lo sé', das otra pista un poco más concreta. "
    "Cuando sea adecuado, validas y cierras con una explicación breve y correcta. "
    "Usa lenguaje claro y amable, en español de España. Para contenido matemático usa LaTeX."
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
    if DECIMAL_RE.search(txt or ""):
        return "decimals"
    low = (txt or "").lower()
    if FRAC2_RE.search(txt or "") or FRAC_MUL_DIV_RE.search(txt or "") or "fracción" in low or "fraccion" in low:
        return "frac"
    if PERCENT_RE.search(txt or "") or "porcent" in low:
        return "percent"
    if is_units_query(txt) or "convert" in low or "convierte" in low:
        return "units"  # (si implementas flow_units)
    if ADD_RE.search(txt or ""):
        return "add"
    if SUB_RE.search(txt or ""):
        return "sub"
    if MUL_RE.search(txt or ""):
        return "mul"
    if DIV_RE.search(txt or ""):
        return "div"
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
            return flow_frac(req.history, user_message)
        if route == "percent":
            return flow_percent(req.history, user_message)
        # Otras asignaturas / preguntas generales
        return llm_reply(req.history, user_message, req.grade or "Primaria")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")), reload=True)
