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

# ---------- Utilidades comunes ----------
def gcd(a: int, b: int) -> int:
    while b: a, b = b, a % b
    return abs(a)

def lcm(a: int, b: int) -> int:
    return abs(a*b)//gcd(a,b) if a and b else 0

def ints(s: str) -> List[int]:
    return [int(x) for x in re.findall(r"-?\d+", s)]

def digits(n: int) -> List[int]:
    return [int(d) for d in str(abs(n))]

def said_no(s: str) -> bool:
    s = s.lower()
    return any(w in s for w in ["no sé","no se","no lo sé","no lo se","no","ni idea"])

def latexify(t: str) -> str:
    t = re.sub(r"(?<!\d)(\d{1,3})\s*/\s*(\d{1,3})(?!\d)", r"$\\frac{\1}{\2}$", t)
    t = re.sub(r"([A-Za-z])\s*\^\s*(\d+)", r"\1^{\2}", t)
    t = t.replace("*", " \\times ")
    return t

def steps_only(text: str) -> List[Step]:
    parts = re.split(r"\s*\d\)\s*", text)
    parts = [p.strip() for p in parts if p.strip()]
    if not parts: return [Step(text=text.strip())]
    return [Step(text=f"{i+1}) {p}") for i,p in enumerate(parts)]

def last_turn(history: List[Dict[str,str]], role: str) -> Optional[Dict[str,str]]:
    for t in reversed(history or []):
        if t.get("role") == role and t.get("content"): return t
    return None

# ---------- Detecciones principales ----------
ADD_RE = re.compile(r"\b(\d{1,6})\s*(?:\+|más)\s*(\d{1,6})\b")
SUB_RE = re.compile(r"\b(\d{1,6})\s*(?:-|menos)\s*(\d{1,6})\b")
MUL_RE = re.compile(r"\b(\d{1,6})\s*(?:×|x|\*)\s*(\d{1,4})\b")     # multiplicador 1–4 cifras
DIV_RE = re.compile(r"\b(\d{1,8})\s*(?:÷|:|\/)\s*(\d{1,4})\b")     # divisor 1–4 cifras (usa ":" o "÷" o "/")
FRAC2_RE = re.compile(r"(?<!\d)(\d{1,3})\s*/\s*(\d{1,3})\s*([+-])\s*(\d{1,3})\s*/\s*(\d{1,3})(?!\d)")
FRAC_MUL_DIV_RE = re.compile(r"(?<!\d)(\d{1,3})\s*/\s*(\d{1,3})\s*(×|x|\*|·|⋅|÷|:)\s*(\d{1,3})\s*/\s*(\d{1,3})(?!\d)")
DECIMAL_RE = re.compile(r"\d+\,\d+|\d+\.\d+")
PERCENT_RE = re.compile(r"\b(\d{1,3})\s*%")
UNITS_WORDS = ["mm","cm","m","km","mg","g","kg","ml","l","seg","s","min","h","horas","metro","gramo","litro"]

GEOM_AREA_RECT = re.compile(r"\b(área|area)\b.*\b(rectángulo|rectangulo|cuadrado)\b", re.I)
GEOM_AREA_TRI = re.compile(r"\b(área|area)\b.*\b(triángulo|triangulo)\b", re.I)
GEOM_AREA_PAR_TRA = re.compile(r"\b(área|area)\b.*\b(paralelogramo|trapecio|trapezoide)\b", re.I)
GEOM_CIRCLE = re.compile(r"\b(circunferencia|perímetro.*círculo|area.*círculo|radio|diámetro)\b", re.I)
GEOM_VOLUME = re.compile(r"\b(volumen)\b.*\b(cubo|prisma)\b", re.I)
STATS_RE = re.compile(r"\b(media|mediana|moda|rango)\b", re.I)
COORD_RE = re.compile(r"\(\s*-?\d+\s*,\s*-?\d+\s*\)")

# ---------- Flujos interactivos (núcleo) ----------
# Suma con llevadas
def flow_add(history: List[Dict[str,str]], msg: str, a: int, b: int) -> ChatResponse:
    la = last_turn(history, "assistant")
    lu = last_turn(history, "user") or {"content": msg}
    a_d = digits(a)[::-1]; b_d = digits(b)[::-1]
    names = ["unidades","decenas","centenas","millares","decenas de millar","centenas de millar"]
    if not la or "unidades" not in la["content"].lower():
        t = (f"1) Sumamos {a} + {b}.\n"
             f"2) Coloca en columnas.\n"
             f"3) **Unidades**: ¿cuánto es {a_d[0]} + {b_d[0]}? Si pasa de 9, escribe la unidad y **lleva** 1.")
        t = latexify(t); return ChatResponse(steps=steps_only(t), reply=t)
    q = la["content"].lower(); idx = 0
    for i,n in enumerate(names):
        if n in q: idx = i; break
    carry_in = 1 if "llevamos 1" in q or "lleva 1" in q else 0
    s = (a_d[idx] if idx < len(a_d) else 0) + (b_d[idx] if idx < len(b_d) else 0) + carry_in
    cdig, ccar = s % 10, s // 10
    nums = ints(lu["content"]); ok = (cdig in nums) and ((ccar==0 and any(w in lu["content"].lower() for w in ["no llevo","no"])) or (ccar in nums))
    if not ok:
        t = (f"1) Revisa **{names[idx]}**. Suma la columna y si ≥10 escribe la **unidad** y lleva 1.\n"
             f"2) ¿Qué escribes y cuánto llevas?")
        t = latexify(t); return ChatResponse(steps=steps_only(t), reply=t)
    next_idx = idx+1
    if next_idx >= max(len(a_d), len(b_d)):
        total = a + b
        t = (f"1) ¡Bien! Completa y revisa.\n"
             f"2) Resultado: **{total}**.\n"
             f"3) ¿Quieres comprobar con una estimación?")
        t = latexify(t); return ChatResponse(steps=steps_only(t), reply=t)
    ad = a_d[next_idx] if next_idx < len(a_d) else 0
    bd = b_d[next_idx] if next_idx < len(b_d) else 0
    carry_phrase = " (recuerda **llevar 1**)" if ccar==1 else ""
    t = (f"1) Perfecto en {names[idx]}.\n"
         f"2) Ahora **{names[next_idx]}**: ¿cuánto es {ad} + {bd}{carry_phrase}? "
         f"Si pasa de 9, ¿qué escribes y cuánto llevas?")
    t = latexify(t); return ChatResponse(steps=steps_only(t), reply=t)

# Resta con préstamo
def flow_sub(history: List[Dict[str,str]], msg: str, a: int, b: int) -> ChatResponse:
    la = last_turn(history, "assistant")
    lu = last_turn(history, "user") or {"content": msg}
    a_d = digits(a)[::-1]; b_d = digits(b)[::-1]
    if not la or "unidades" not in la["content"].lower():
        t = (f"1) Restamos {a} − {b}.\n"
             f"2) **Unidades**: ¿puedes hacer {a_d[0]} − {b_d[0]}? "
             f"Si no, ¿qué hacemos?")
        t = latexify(t); return ChatResponse(steps=steps_only(t), reply=t)
    q = la["content"].lower()
    if "¿qué hacemos?" in q:
        if any(w in lu["content"].lower() for w in ["pedir", "prést", "prest", "tomar", "llevar"]):
            t = ("1) ¡Eso es! **Pedimos 1 decena** y la convertimos en 10 unidades.\n"
                 "2) Ahora resta unidades. ¿Resultado en unidades y qué queda en decenas?")
            t = latexify(t); return ChatResponse(steps=steps_only(t), reply=t)
        else:
            t = ("1) Cuando no puedes restar, **pide prestado** a la columna de al lado (1 decena = 10 unidades).\n"
                 "2) Inténtalo: ¿qué haces en unidades?")
            t = latexify(t); return ChatResponse(steps=steps_only(t), reply=t)
    if any(ch.isdigit() for ch in lu["content"]):
        t = ("1) Bien. Pasa a **decenas** (aplica el préstamo si lo hiciste).\n"
             "2) Luego **centenas** si hay.")
        t = latexify(t); return ChatResponse(steps=steps_only(t), reply=t)
    t = "1) Repite la resta en unidades y di el resultado (o explica si necesitas pedir)."
    t = latexify(t); return ChatResponse(steps=steps_only(t), reply=t)

# ---------- Multiplicación 1 cifra y multi-cifra ----------
def flow_mul_single(history: List[Dict[str,str]], msg: str, a: int, d: int) -> ChatResponse:
    la = last_turn(history, "assistant")
    lu = last_turn(history, "user") or {"content": msg}
    a_d = digits(a)[::-1]
    if not la or "unidades" not in la["content"].lower():
        t = (f"1) Multiplicamos {a} × {d}.\n"
             f"2) **Unidades**: ¿cuánto es {a_d[0]} × {d}? Si es ≥10, escribe la unidad y **lleva** la decena.")
        t = latexify(t); return ChatResponse(steps=steps_only(t), reply=t)
    if any(ch.isdigit() for ch in lu["content"]):
        if len(a_d) >= 2:
            t = (f"1) Ahora **decenas**: {a_d[1]} × {d} (+ lo que llevas si hubo).\n"
                 f"2) ¿Qué escribes y cuánto llevas?")
        else:
            t = ("1) Ya no hay más columnas. Escribe el resultado completo.\n"
                 "2) ¿Qué número obtuviste?")
        t = latexify(t); return ChatResponse(steps=steps_only(t), reply=t)
    t = "1) Di el resultado de unidades × multiplicador (y si llevas)."
    t = latexify(t); return ChatResponse(steps=steps_only(t), reply=t)

def flow_mul_multi(history: List[Dict[str,str]], msg: str, a: int, m: int) -> ChatResponse:
    # Estado por etapas: P0 (unidades), P1 (decenas), P2 (centenas) ... y suma final
    la = last_turn(history, "assistant")
    lu = last_turn(history, "user") or {"content": msg}
    md = digits(m)[::-1]  # LSD→MSD
    # ¿en qué etapa estamos? buscamos la última pista
    stage = 0
    if la:
        lc = la["content"].lower()
        if "parcial por unidades" in lc: stage = 0
        if "parcial por decenas" in lc: stage = 1
        if "parcial por centenas" in lc: stage = 2
        if "parcial por millares" in lc: stage = 3
        if "suma de parciales" in lc: stage = 99
        # si el último prompt pedía un parcial concreto, ahora evaluamos ese parcial
        # Evaluación
        if "parcial por " in lc and "escríbelo" in lc:
            # esperamos el parcial anterior correcto
            expected = a * md[stage] * (10**stage)
            if said_no(lu["content"]):
                hint = (
                    f"1) Multiplica {a} × {md[stage]}. "
                    f"2) Añade {'un 0' if stage==1 else ('dos 0' if stage==2 else (str(stage)+' ceros'))} al final porque es la posición.\n"
                    f"3) Escríbelo sin sumar aún."
                )
                hint = latexify(hint); return ChatResponse(steps=steps_only(hint), reply=hint)
            nums = ints(lu["content"])
            if expected in nums:
                # Avanzamos a la siguiente etapa
                next_stage = stage + 1
                if next_stage >= len(md):
                    # pedir suma final
                    parciales = [a * md[i]*(10**i) for i in range(len(md))]
                    t = (f"1) Perfecto. Ya tenemos todos los parciales: {', '.join(map(str, parciales))}.\n"
                         f"2) **Suma de parciales**: súmalos para obtener el producto total.\n"
                         f"3) ¿Cuál es el resultado final?")
                    t = latexify(t); return ChatResponse(steps=steps_only(t), reply=t)
                else:
                    name = ["unidades","decenas","centenas","millares","decenas de millar"][next_stage]
                    digit = md[next_stage]
                    zeros = " (añade " + ("1 cero" if next_stage==1 else f"{next_stage} ceros") + ") " if next_stage>=1 else ""
                    t = (f"1) Bien ese parcial.\n"
                         f"2) **Parcial por {name}** (dígito {digit}){zeros}: calcula {a} × {digit} y desplázalo según la posición.\n"
                         f"3) Escríbelo (sin sumar todavía).")
                    t = latexify(t); return ChatResponse(steps=steps_only(t), reply=t)
            else:
                # parcial incorrecto
                t = (
                    f"1) Revisa: {a} × {md[stage]} y luego desplaza {stage} posiciones (añadiendo ceros).\n"
                    f"2) Escribe ese **parcial** solamente."
                )
                t = latexify(t); return ChatResponse(steps=steps_only(t), reply=t)
        if "suma de parciales" in lc:
            expected_total = a * m
            if said_no(lu["content"]):
                t = (
                    "1) Suma en columna los parciales alineando las posiciones.\n"
                    "2) Si supera 9 en una columna, lleva 1 a la siguiente.\n"
                    "3) Inténtalo y dime el total."
                )
                t = latexify(t); return ChatResponse(steps=steps_only(t), reply=t)
            nums = ints(lu["content"])
            if expected_total in nums:
                t = (f"1) ¡Muy bien! El resultado es **{expected_total}**.\n"
                     f"2) ¿Quieres probar otra multiplicación?")
                t = latexify(t); return ChatResponse(steps=steps_only(t), reply=t)
            else:
                t = ("1) Revisa la suma de parciales. Alinea unidades/decenas/centenas.\n"
                     "2) ¿Cuál te sale ahora?")
                t = latexify(t); return ChatResponse(steps=steps_only(t), reply=t)
    # Inicio (sin etapa previa)
    name = "unidades"; digit = md[0]
    t = (f"1) Multiplicamos {a} × {m}.\n"
         f"2) **Parcial por {name}** (dígito {digit}): calcula {a} × {digit} (sin sumar aún).\n"
         f"3) Escríbelo.")
    t = latexify(t); return ChatResponse(steps=steps_only(t), reply=t)

def flow_mul(history: List[Dict[str,str]], msg: str, a: int, m: int) -> ChatResponse:
    if m < 10:
        return flow_mul_single(history, msg, a, m)
    return flow_mul_multi(history, msg, a, m)

# ---------- División 1 cifra y multi-cifra ----------
def precompute_division_steps(n: int, d: int) -> List[Tuple[int,int,int]]:
    """
    Devuelve lista de pasos (block, q_digit, remainder) para división larga n ÷ d.
    Cada paso usa el bloque mínimo actual (resto*10 + siguiente cifra(s) según necesidad).
    """
    s = str(n)
    steps = []
    i = 0
    # primer bloque: el menor prefijo ≥ d
    if int(s[0]) >= d:
        block = int(s[0]); i = 1
    else:
        block = int(s[:2]); i = 2
    while True:
        q = block // d
        r = block - q*d
        steps.append((block, q, r))
        if i >= len(s):
            break
        block = r*10 + int(s[i])
        i += 1
        # si aún es menor que d y quedan más cifras, arrastra más
        while block < d and i < len(s):
            steps.append((block, 0, block))  # cociente 0 en este subpaso
            block = block*10 + int(s[i])
            i += 1
    return steps

def count_div_prompts(history: List[Dict[str,str]]) -> int:
    return sum(1 for t in history or [] if t.get("role")=="assistant" and "¿cuántas veces cabe" in t.get("content","").lower())

def flow_div_multi(history: List[Dict[str,str]], msg: str, n: int, d: int) -> ChatResponse:
    la = last_turn(history, "assistant")
    lu = last_turn(history, "user") or {"content": msg}
    steps = precompute_division_steps(n, d)
    done = count_div_prompts(history)  # cuántos bloques ya preguntados

    # si ya hemos preguntado por todos los bloques, pedimos el total
    if done >= len(steps):
        q_digits = [str(q) for (_,q,_) in steps]
        expected_q = int("".join(q_digits))
        expected_r = steps[-1][2]
        if said_no(lu["content"]):
            t = ("1) Une los cocientes parciales en orden para el **cociente**.\n"
                 "2) El **resto** es el último resto que te quedó.\n"
                 "3) ¿Qué cociente y resto obtienes?")
            t = latexify(t); return ChatResponse(steps=steps_only(t), reply=t)
        nums = ints(lu["content"])
        ok_q = (expected_q in nums)
        ok_r = (expected_r in nums)
        if ok_q and ok_r:
            t = (f"1) ¡Muy bien! Cociente **{expected_q}** y resto **{expected_r}**.\n"
                 "2) ¿Probamos otra división?")
            t = latexify(t); return ChatResponse(steps=steps_only(t), reply=t)
        else:
            t = ("1) Revisa: el cociente se forma con los dígitos de cada paso.\n"
                 "2) El resto final es el último que te quedó.\n"
                 "3) Dime cociente y resto.")
            t = latexify(t); return ChatResponse(steps=steps_only(t), reply=t)

    # paso actual
    block, qexp, rexp = steps[done]
    # ¿ya preguntamos el resto? detecta por presencia de "resta" en el prompt anterior
    asked_remainder = la and "resta" in la["content"].lower() and "resto" in la["content"].lower()

    if not la or not asked_remainder:
        # Pregunta por cociente y resto del bloque actual (en uno)
        t = (f"1) Paso de división {done+1}/{len(steps)}. **Bloque actual: {block}**.\n"
             f"2) ¿Cuántas veces **cabe** {d} en {block}? Di el cociente **y** el resto tras restar.")
        t = latexify(t); return ChatResponse(steps=steps_only(t), reply=t)

    # Evaluación del paso actual (si venimos de haber preguntado por resto)
    if said_no(lu["content"]):
        # pista con múltiplos cercanos
        mults = ", ".join(str(d*i) for i in range(max(1,qexp-2), qexp+3))
        t = (f"1) Mira los múltiplos de {d} cercanos a {block}: {mults}…\n"
             f"2) Elige el mayor que **no supere** {block} y resta para hallar el resto.\n"
             f"3) Dime cociente y resto.")
        t = latexify(t); return ChatResponse(steps=steps_only(t), reply=t)

    nums = ints(lu["content"])
    ok_q = qexp in nums
    ok_r = rexp in nums
    if ok_q and ok_r:
        # Avanza al siguiente bloque (la siguiente vez done habrá subido por el nuevo prompt)
        if done+1 == len(steps):
            t = ("1) Bien. Ya no quedan cifras por bajar.\n"
                 "2) Une los cocientes parciales para obtener el cociente y di también el resto final.")
        else:
            next_block = steps[done+1][0]
            t = (f"1) ¡Correcto! Baja la siguiente cifra.\n"
                 f"2) **Bloque actual: {next_block}**. ¿Cuántas veces cabe {d}? Di cociente y resto.")
        t = latexify(t); return ChatResponse(steps=steps_only(t), reply=t)
    else:
        t = (f"1) Revisa este bloque {block}: busca el múltiplo de {d} que no se pase.\n"
             f"2) Dime cociente y resto.")
        t = latexify(t); return ChatResponse(steps=steps_only(t), reply=t)

def flow_div(history: List[Dict[str,str]], msg: str, n: int, d: int) -> ChatResponse:
    # 1 cifra → mismo flujo (la heurística multi gestiona ambos)
    return flow_div_multi(history, msg, n, d)

# ---------- Decimales ----------
def flow_decimals(history: List[Dict[str,str]], msg: str) -> ChatResponse:
    l = msg.lower()
    if "×" in msg or "x" in msg or "*" in msg:
        t = ("1) Cuenta las cifras decimales de los factores.\n"
             "2) Multiplica como enteros.\n"
             "3) Coloca la coma sumando las cifras decimales totales.\n"
             "4) ¿Cuántas cifras decimales deben quedar?")
        t = latexify(t); return ChatResponse(steps=steps_only(t), reply=t)
    if "÷" in msg or ":" in msg:
        t = ("1) Si divides por natural: divide como enteros.\n"
             "2) Coloca la coma en el cociente alineada con el dividendo.\n"
             "3) Por 10/100/1000: mueve la coma a la izquierda.\n"
             "4) ¿Cuál sería el primer paso aquí?")
        t = latexify(t); return ChatResponse(steps=steps_only(t), reply=t)
    t = ("1) **Alinea las comas**.\n"
         "2) Completa con ceros si faltan decimales.\n"
         "3) Suma/resta por columnas.\n"
         "4) ¿Qué escribes en la primera columna decimal?")
    t = latexify(t); return ChatResponse(steps=steps_only(t), reply=t)

# ---------- Fracciones ----------
def flow_frac(history: List[Dict[str,str]], msg: str) -> ChatResponse:
    m2 = FRAC2_RE.search(msg)
    if m2:
        a,b,op,c,dn = int(m2.group(1)), int(m2.group(2)), m2.group(3), int(m2.group(4)), int(m2.group(5))
        la = last_turn(history, "assistant")
        asked = la and ("MCM" in la["content"] or "mínimo común" in la["content"].lower())
        if not asked:
            t = (f"1) Resolvamos $\\frac{{{a}}}{{{b}}} {op} \\frac{{{c}}}{{{dn}}}$.\n"
                 f"2) **Pista**: busca el **MCM** de {b} y {dn}. ¿Cuál es?")
            t = latexify(t); return ChatResponse(steps=steps_only(t), reply=t)
        expected = lcm(b,dn)
        lu = last_turn(history,"user") or {"content": msg}
        if said_no(lu["content"]):
            t = (f"1) El MCM es el primer número común de las tablas de {b} y {dn}.\n"
                 f"2) Escribe múltiplos de ambos y busca el primero que coincide.\n"
                 f"3) ¿Cuál te sale?")
            t = latexify(t); return ChatResponse(steps=steps_only(t), reply=t)
        if expected in ints(lu["content"]):
            k1, k2 = expected//b, expected//dn
            t = (f"1) Con denominador {expected}, "
                 f"$\\frac{{{a}}}{{{b}}}\\to\\frac{{{a*k1}}}{{{expected}}}$ y "
                 f"$\\frac{{{c}}}{{{dn}}}\\to\\frac{{{c*k2}}}{{{expected}}}$.\n"
                 f"2) Ahora opera numeradores y **simplifica** si procede. ¿Resultado?")
            t = latexify(t); return ChatResponse(steps=steps_only(t), reply=t)
        t = ("1) Revisa los múltiplos y encuentra el primero común.\n"
             "2) Pista: si son coprimos, el MCM es su producto.")
        t = latexify(t); return ChatResponse(steps=steps_only(t), reply=t)
    mmd = FRAC_MUL_DIV_RE.search(msg)
    if mmd:
        a,b,op,c,dn = int(mmd.group(1)),int(mmd.group(2)),mmd.group(3),int(mmd.group(4)),int(mmd.group(5))
        if op in ["×","x","*","·","⋅"]:
            t = (f"1) Multiplicación: numerador×numerador, denominador×denominador.\n"
                 f"2) ¿Cuánto da $\\frac{{{a}}}{{{b}}} \\times \\frac{{{c}}}{{{dn}}}$? Luego **simplifica**.")
        else:
            t = (f"1) División: multiplica por la inversa.\n"
                 f"2) ¿Cuál es $\\frac{{{a}}}{{{b}}} \\div \\frac{{{c}}}{{{dn}}}$ tras invertir la segunda? "
                 f"Después **simplifica**.")
        t = latexify(t); return ChatResponse(steps=steps_only(t), reply=t)
    if any(k in msg.lower() for k in ["equival", "igual", "simplif", "mínima", "minima", "reduc"]):
        t = ("1) Para equivalentes, multiplica o divide numerador y denominador por el **mismo número**.\n"
             "2) Para simplificar, divide entre el **MCD**.\n"
             "3) ¿Qué número usarías aquí?")
        t = latexify(t); return ChatResponse(steps=steps_only(t), reply=t)
    t = ("1) ¿Qué necesitas con fracciones: comparar, ordenar, sumar/restar, multiplicar o dividir?\n"
         "2) Escríbelo con un ejemplo.")
    t = latexify(t); return ChatResponse(steps=steps_only(t), reply=t)

# ---------- Porcentajes / razones ----------
def flow_percent(history: List[Dict[str,str]], msg: str) -> ChatResponse:
    if "de" in msg and "%" in msg:
        m = re.findall(r"(\d+)\s*%\s*de\s*(\d+)", msg)
        if m:
            p, n = int(m[0][0]), int(m[0][1])
            t = (f"1) Convierte {p}% a decimal: {p}/100.\n"
                 f"2) Multiplica: {p}/100 × {n}.\n"
                 f"3) ¿Cuál es el resultado?")
            t = latexify(t); return ChatResponse(steps=steps_only(t), reply=t)
    if "qué porcentaje" in msg.lower() or "que porcentaje" in msg.lower():
        vals = ints(msg)
        if len(vals) >= 2:
            a, b = vals[0], vals[1]
            t = (f"1) Divide: {a} ÷ {b}.\n"
                 f"2) Multiplica por 100 para el %.\n"
                 f"3) ¿Qué valor te sale?")
            t = latexify(t); return ChatResponse(steps=steps_only(t), reply=t)
    if any(k in msg.lower() for k in ["proporc", "razón", "razon"]):
        t = ("1) Escribe la proporción como fracción y **simplifica**.\n"
             "2) Completa la tabla o usa regla de tres si falta un valor.\n"
             "3) ¿Qué valor buscas?")
        t = latexify(t); return ChatResponse(steps=steps_only(t), reply=t)
    if "%" in msg or "decimal" in msg.lower() or "fracción" in msg.lower() or "fraccion" in msg.lower():
        t = ("1) % ↔ fracción: p/100.\n"
             "2) % ↔ decimal: mueve la coma 2 posiciones.\n"
             "3) ¿Qué conversión necesitas?")
        t = latexify(t); return ChatResponse(steps=steps_only(t), reply=t)
    t = "1) Dime si quieres calcular un porcentaje, convertir entre %, fracción y decimal, o resolver una proporción."
    t = latexify(t); return ChatResponse(steps=steps_only(t), reply=t)

# ---------- Teoría de números ----------
def flow_number_theory(history: List[Dict[str,str]], msg: str) -> ChatResponse:
    l = msg.lower()
    if "múltipl" in l or "multiplo" in l:
        n = ints(msg)[0] if ints(msg) else None
        t = (f"1) Los múltiplos de {n} son {n}, {n*2}, {n*3}, …\n"
             "2) ¿Cuál necesitas?")
        t = latexify(t); return ChatResponse(steps=steps_only(t), reply=t)
    if "factor" in l and "prima" not in l:
        n = ints(msg)[0] if ints(msg) else None
        t = (f"1) Busca números que **dividan exacto** a {n}.\n"
             "2) Enuméralos por parejas.\n"
             "3) ¿Qué factores encuentras?")
        t = latexify(t); return ChatResponse(steps=steps_only(t), reply=t)
    if "primo" in l or "compuesto" in l:
        n = ints(msg)[0] if ints(msg) else None
        t = (f"1) Un **primo** tiene solo 2 divisores (1 y él mismo).\n"
             f"2) Prueba a dividir {n} entre 2, 3, 5…\n"
             "3) ¿Encuentras algún divisor además de 1 y él mismo?")
        t = latexify(t); return ChatResponse(steps=steps_only(t), reply=t)
    if "factorización" in l or "primos" in l:
        n = ints(msg)[0] if ints(msg) else None
        t = (f"1) Divide {n} por el **menor primo** posible (2, 3, 5…).\n"
             "2) Repite con el cociente hasta llegar a 1.\n"
             "3) Escríbelo como producto de primos.")
        t = latexify(t); return ChatResponse(steps=steps_only(t), reply=t)
    if "mcd" in l or "máximo común" in l:
        a,b = ints(msg)[:2]
        t = (f"1) Lista factores de {a} y de {b}.\n"
             "2) Elige el **mayor** común.\n"
             "3) ¿Cuál te sale?")
        t = latexify(t); return ChatResponse(steps=steps_only(t), reply=t)
    if "mcm" in l or "mínimo común" in l:
        a,b = ints(msg)[:2]
        t = (f"1) Lista múltiplos de {a} y de {b}.\n"
             "2) Elige el **primero** común.\n"
             "3) ¿Cuál te sale?")
        t = latexify(t); return ChatResponse(steps=steps_only(t), reply=t)
    if "secuencia" in l or "progresión" in l or "aritmética" in l or "geométrica" in l:
        t = ("1) Aritmética: suma una **diferencia** fija.\n"
             "2) Geométrica: multiplica por una **razón** fija.\n"
             "3) ¿Qué diferencia/razón hay en tu lista?")
        t = latexify(t); return ChatResponse(steps=steps_only(t), reply=t)
    return ChatResponse(steps=steps_only("1) ¿Múltiplos, factores, primo/compuesto, MCD, MCM o secuencias? 2) Pon un ejemplo."), reply="")

# ---------- Unidades ----------
def flow_units(history: List[Dict[str,str]], msg: str) -> ChatResponse:
    l = msg.lower()
    if any(u in l for u in ["km","m","cm","mm"]):
        t = ("1) Escala métrica: km → m → cm → mm (×10 / ÷10 por paso).\n"
             "2) ¿Convertimos de qué a qué?")
    elif any(u in l for u in ["kg","g","mg"]):
        t = ("1) Masa: kg ↔ g ↔ mg (×1000/÷1000 por salto grande).\n"
             "2) ¿De qué a qué convertimos?")
    elif any(u in l for u in ["l","ml","litro"]):
        t = ("1) Capacidad: l ↔ ml (×1000/÷1000).\n"
             "2) ¿De qué a qué?")
    elif any(u in l for u in ["seg","s","min","h","hora"]):
        t = ("1) Tiempo: 60 s = 1 min; 60 min = 1 h.\n"
             "2) ¿Qué conversión necesitas?")
    else:
        t = "1) Dime la magnitud (longitud/masa/capacidad/tiempo) y los valores a convertir."
    t = latexify(t); return ChatResponse(steps=steps_only(t), reply=t)

# ---------- Geometría / Medición ----------
GEOM_AREA_RECT = re.compile(r"\b(área|area)\b.*\b(rectángulo|rectangulo|cuadrado)\b", re.I)
GEOM_AREA_TRI = re.compile(r"\b(área|area)\b.*\b(triángulo|triangulo)\b", re.I)
GEOM_AREA_PAR_TRA = re.compile(r"\b(área|area)\b.*\b(paralelogramo|trapecio|trapezoide)\b", re.I)
GEOM_CIRCLE = re.compile(r"\b(circunferencia|perímetro.*círculo|area.*círculo|radio|diámetro)\b", re.I)
GEOM_VOLUME = re.compile(r"\b(volumen)\b.*\b(cubo|prisma)\b", re.I)

def flow_geometry(history: List[Dict[str,str]], msg: str) -> ChatResponse:
    l = msg.lower()
    if GEOM_AREA_RECT.search(l):
        t = ("1) Área rectángulo/cuadrado: $A=base\\times altura$.\n"
             "2) ¿Qué valores tienes? Multiplica.")
    elif GEOM_AREA_TRI.search(l):
        t = ("1) Área triángulo: $A=\\frac{base\\times altura}{2}$.\n"
             "2) ¿Qué base y altura usas?")
    elif GEOM_AREA_PAR_TRA.search(l):
        t = ("1) Paralelogramo: $A=b\\times h$. Trapecio: $A=\\frac{(B+b)\\times h}{2}$.\n"
             "2) ¿Qué datos tienes?")
    elif GEOM_CIRCLE.search(l):
        t = ("1) Circunferencia: $C=2\\pi r$; Área: $A=\\pi r^{2}$.\n"
             "2) ¿Cuál es el radio o el diámetro?")
    elif GEOM_VOLUME.search(l):
        t = ("1) Volumen cubo: $V=a^{3}$. Prisma rectangular: $V= largo\\times ancho\\times alto$.\n"
             "2) ¿Qué medidas tienes?")
    else:
        t = ("1) Dime si buscas **perímetro**, **área** (qué figura), partes del círculo o **volumen** y los datos.")
    t = latexify(t); return ChatResponse(steps=steps_only(t), reply=t)

# ---------- Estadística / Probabilidad ----------
STATS_RE = re.compile(r"\b(media|mediana|moda|rango)\b", re.I)
def flow_stats_prob(history: List[Dict[str,str]], msg: str) -> ChatResponse:
    l = msg.lower()
    if STATS_RE.search(l):
        t = ("1) **Media**: suma y divide entre el nº de datos.\n"
             "2) **Mediana**: ordena y toma el central (o promedio de los dos centrales).\n"
             "3) **Moda**: el que más se repite. **Rango**: max − min.\n"
             "4) Dame tus datos.")
        t = latexify(t); return ChatResponse(steps=steps_only(t), reply=t)
    t = ("1) Probabilidad: casos favorables / casos posibles.\n"
         "2) Para sucesos compuestos, multiplica si son independientes.\n"
         "3) ¿Cuál es el experimento y los casos?")
    t = latexify(t); return ChatResponse(steps=steps_only(t), reply=t)

# ---------- Plano de coordenadas ----------
def flow_coordinates(history: List[Dict[str,str]], msg: str) -> ChatResponse:
    m = COORD_RE.search(msg)
    if m:
        x,y = ints(m.group(0))
        quad = ("I" if x>0 and y>0 else
                "II" if x<0 and y>0 else
                "III" if x<0 and y<0 else
                "IV" if x>0 and y<0 else "eje")
        t = (f"1) Punto ({x}, {y}).\n"
             f"2) Recuerda: x horizontal, y vertical.\n"
             f"3) Este punto está en el **cuadrante {quad}** (o en un eje si x=0 o y=0).\n"
             f"4) ¿Quieres ubicar otro punto?")
        t = latexify(t); return ChatResponse(steps=steps_only(t), reply=t)
    t = ("1) Escribe un punto como (x, y).\n"
         "2) Te digo en qué cuadrante está y cómo ubicarlo.")
    t = latexify(t); return ChatResponse(steps=steps_only(t), reply=t)

# ---------- Orden de las operaciones / Enteros ----------
def flow_order_ops(history: List[Dict[str,str]], msg: str) -> ChatResponse:
    t = ("1) Orden: **Paréntesis → Exponentes → Multiplicación/División → Suma/Resta** (de izquierda a derecha).\n"
         "2) Señala qué se resuelve primero en tu expresión.")
    t = latexify(t); return ChatResponse(steps=steps_only(t), reply=t)

def flow_integers(history: List[Dict[str,str]], msg: str) -> ChatResponse:
    t = ("1) Signos: **+ con +** suma; **− con −** suma y pone +; **+ con −** resta y toma el signo del mayor absoluto.\n"
         "2) Multiplicación/división: signos iguales → +; distintos → −.\n"
         "3) Dame tu operación con enteros.")
    t = latexify(t); return ChatResponse(steps=steps_only(t), reply=t)

# ---------- Router principal ----------
def detect_route(history: List[Dict[str,str]], msg: str) -> str:
    txt = msg
    if DECIMAL_RE.search(txt): return "decimals"
    if FRAC2_RE.search(txt) or FRAC_MUL_DIV_RE.search(txt) or "fracción" in txt.lower() or "fraccion" in txt.lower(): return "frac"
    if PERCENT_RE.search(txt) or "porcent" in txt.lower() or "proporc" in txt.lower(): return "percent"
    if any(w in txt.lower() for w in ["múltipl", "multiplo", "factor", "primo", "compuesto", "mcd", "mcm", "secuencia", "aritmética", "geométrica"]): return "numtheory"
    if any(u in txt.lower() for u in UNITS_WORDS) or "convert" in txt.lower(): return "units"
    if GEOM_AREA_RECT.search(txt) or GEOM_AREA_TRI.search(txt) or GEOM_AREA_PAR_TRA.search(txt) or GEOM_CIRCLE.search(txt) or GEOM_VOLUME.search(txt) or "perímetro" in txt.lower() or "perimetro" in txt.lower(): return "geometry"
    if STATS_RE.search(txt) or "probabilidad" in txt.lower(): return "stats"
    if COORD_RE.search(txt) or "coordenad" in txt.lower() or "cuadrante" in txt.lower(): return "coords"
    if "orden de las operaciones" in txt.lower() or "prioridad de operaciones" in txt.lower(): return "orderops"
    if "entero" in txt.lower(): return "integers"
    if ADD_RE.search(txt): return "add"
    if SUB_RE.search(txt): return "sub"
    if MUL_RE.search(txt): return "mul"
    if DIV_RE.search(txt): return "div"
    return "llm"

# ---------- LLM fallback ----------
SYSTEM_PROMPT = (
    "Eres Tutorín (6.º Primaria, España). Responde SIEMPRE en pasos numerados breves y termina con **UNA** pregunta. "
    "Usa LaTeX para fracciones y fórmulas. No des resultados finales de golpe si puedes guiar."
)

def llm_reply(history: List[Dict[str,str]], user_message: str, grade: str) -> ChatResponse:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for t in history or []:
        r,c = t.get("role",""), t.get("content","")
        if r in {"user","assistant"} and c: messages.append({"role": r, "content": c})
    messages.append({"role": "user", "content": f"Curso: {grade}\nAlumno: {user_message}"} )
    out = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL","gpt-4o-mini"),
        temperature=0.2,
        messages=messages,
    )
    reply = (out.choices[0].message.content or "").strip()
    reply = latexify(reply)
    return ChatResponse(steps=steps_only(reply), reply=reply)

# ---------- Endpoints ----------
@app.get("/ping")
def ping():
    return {"ok": True, "message": "Tutorín está vivo 👋"}

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(status_code=500, detail="Falta OPENAI_API_KEY en el servidor.")
    user_message = (req.message or req.text or "").strip()
    grade = (req.grade or "Primaria").strip()
    history = req.history or []
    if not user_message:
        raise HTTPException(status_code=400, detail="El campo 'message'/'text' está vacío.")

    route = detect_route(history, user_message)
    try:
        if route == "add":
            a,b = map(int, ADD_RE.search(user_message).groups())
            return flow_add(history, user_message, a, b)
        if route == "sub":
            a,b = map(int, SUB_RE.search(user_message).groups())
            return flow_sub(history, user_message, a, b)
        if route == "mul":
            a,m = map(int, MUL_RE.search(user_message).groups())
            return flow_mul(history, user_message, a, m)
        if route == "div":
            n,d = map(int, DIV_RE.search(user_message).groups())
            return flow_div(history, user_message, n, d)
        if route == "decimals":
            return flow_decimals(history, user_message)
        if route == "frac":
            return flow_frac(history, user_message)
        if route == "percent":
            return flow_percent(history, user_message)
        if route == "numtheory":
            return flow_number_theory(history, user_message)
        if route == "units":
            return flow_units(history, user_message)
        if route == "geometry":
            return flow_geometry(history, user_message)
        if route == "stats":
            return flow_stats_prob(history, user_message)
        if route == "coords":
            return flow_coordinates(history, user_message)
        if route == "orderops":
            return flow_order_ops(history, user_message)
        if route == "integers":
            return flow_integers(history, user_message)
        return llm_reply(history, user_message, grade)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")

# Local run
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT","8000")), reload=True)
