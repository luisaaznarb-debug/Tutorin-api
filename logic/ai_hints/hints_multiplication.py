# -*- coding: utf-8 -*-
"""
hints_multiplication.py
Pistas progresivas para multiplicación según nivel de error.
Compatible con multiplication_engine.py
"""

from .hints_utils import _extract_pre_block, _question, _first_int_on_line
import re
from typing import Optional, List

# ────────── Utilidades ──────────
def _parse_mult_from_context(ctx: str):
    """Extrae los dos números de una multiplicación del contexto."""
    lines = _extract_pre_block(ctx).splitlines()
    if len(lines) < 2:
        return None
    a = _first_int_on_line(lines[0])
    b = _first_int_on_line(lines[1])
    if a is None or b is None:
        return None
    return (a, b)

def _explain_long_mult_by_digit(a: int, digit: int) -> str:
    """
    Explica paso a paso la multiplicación de 'a' por 'digit',
    mostrando las llevadas en cada posición.
    """
    s = str(a)
    carry = 0
    steps: List[str] = []
    
    for ch in reversed(s):
        d = int(ch)
        subtotal = d * digit + carry
        write = subtotal % 10
        prev = carry
        carry = subtotal // 10
        
        if prev > 0:
            steps.append(
                f"{d}×{digit} + {prev} = {subtotal} → escribe <b>{write}</b>" + 
                (f" y llevas <b>{carry}</b>" if carry else "")
            )
        else:
            steps.append(
                f"{d}×{digit} = {d*digit} → escribe <b>{write}</b>" + 
                (f" y llevas <b>{carry}</b>" if carry else "")
            )
    
    steps_text = "; luego ".join(steps)
    
    if carry:
        steps_text += f"; al final, escribe <b>{carry}</b> a la izquierda"
    
    return steps_text + "."

def _asks_where_to_start(txt: str) -> bool:
    """Detecta si el alumno pregunta por dónde empezar."""
    if not txt: 
        return False
    t = txt.lower()
    return any(p in t for p in [
        "por qué número empie", "por que numero empie",
        "qué número empie", "que numero empie",
        "por dónde empie", "por donde empie",
        "dónde empie", "donde empie",
        "empiezo por"
    ])

# ────────── Pistas progresivas ──────────
def _mult_parcial_hint(context: str, err: int, cycle: str) -> str:
    """
    Pistas para calcular líneas parciales de multiplicación.
    Niveles:
    - 1: pista básica
    - 2: recordatorio personalizado
    - 3: explicación con llevadas
    - 4+: casi-solución
    """
    # ¿El alumno pregunta "por qué número empiezo"?
    if _asks_where_to_start(context):
        parsed = _parse_mult_from_context(context)
        if parsed:
            a, b = parsed
            return (
                f"Empieza por la <b>cifra de las unidades</b> del número de abajo "
                f"porque es la que vale menos. En <b>{a} × {b}</b>, esa cifra es "
                f"<b>{str(b)[-1]}</b>. Después pasarás a decenas, centenas…"
            )
        return (
            "Empieza por la <b>cifra de las unidades</b> del número de abajo. "
            "Luego pasarás a decenas y centenas, añadiendo ceros por la posición."
        )

    parsed = _parse_mult_from_context(context)
    if not parsed:
        return "👉 Multiplica el número de arriba por cada cifra del número de abajo."

    a, b = parsed

    # Detectar la cifra con la que se multiplica
    m_digit = re.search(r"que es\s*(\d+)", context, flags=re.IGNORECASE)
    digit = int(m_digit.group(1)) if m_digit else int(str(b)[-1])

    # Detectar desplazamiento (decenas/centenas)
    shift = 0
    m_line = re.search(r"línea parcial #(\d+)", context)
    if m_line:
        n_line = int(m_line.group(1))
        shift = max(0, n_line - 1)

    # Nivel 1: pista básica
    if err == 1:
        return (
            f"👉 Multiplica <b>{a}</b> por la cifra de las <b>unidades</b> del número de abajo "
            f"(<b>{str(b)[-1]}</b>) y escribe esa <b>línea parcial</b>. "
            + _question("¿Qué resultado obtienes?")
        )

    # Nivel 2: recordatorio personalizado
    if err == 2:
        base = f"Multiplica <b>{a}</b> por <b>{digit}</b> y escribe esa <b>línea parcial</b>."
        if shift > 0:
            ceros = "cero" if shift == 1 else "ceros"
            base += f" Como es la línea #{shift+1}, añade <b>{shift}</b> {ceros} al final (desplazamiento)."
        else:
            base += " En la primera línea no hace falta desplazar."
        return base + " " + _question("¿Cuál es el resultado?")

    # Nivel 3: explicación con llevadas
    if err == 3:
        detail = _explain_long_mult_by_digit(a, digit)
        tail = ""
        if shift > 0:
            ceros = "cero" if shift == 1 else "ceros"
            tail = f" Después añade <b>{shift}</b> {ceros} al final por la posición."
        return "💡 " + detail + tail

    # Nivel 4+: casi-solución
    if err >= 4:
        detail = _explain_long_mult_by_digit(a, digit)
        parcial = a * digit
        if shift > 0:
            ceros = "cero" if shift == 1 else "ceros"
            return (
                f"La línea parcial es <b>{parcial}</b> (resultado de <b>{a}×{digit}</b>). {detail} "
                f"Luego añade <b>{shift}</b> {ceros} por la posición y escribe: <b>{parcial}{'0'*shift}</b>."
            )
        return f"La línea parcial es <b>{parcial}</b> (resultado de <b>{a}×{digit}</b>). {detail}"

    return "Escribe la línea parcial multiplicando por la cifra de <b>unidades</b> del número de abajo."

def _mult_suma_hint(context: str, err: int, cycle: str) -> str:
    """Pistas para sumar las líneas parciales."""
    if err == 1:
        return (
            "👉 Ahora suma todas las líneas parciales que has calculado. "
            "Recuerda alinearlas por la <b>derecha</b> y sumar columna por columna. "
            + _question("¿Qué total obtienes?")
        )
    
    if err == 2:
        return (
            "🧮 Alinea las líneas parciales por la <b>derecha</b> y suma en vertical. "
            "Ten cuidado con las llevadas cuando la suma de una columna pase de 9. "
            + _question("¿Cuál es el resultado final?")
        )
    
    if err == 3:
        return (
            "💡 Haz una <b>estimación</b> para comprobar: redondea ambos números y multiplica mentalmente. "
            "Si tu resultado está muy lejos, revisa la suma de las líneas parciales. "
            + _question("¿Tiene sentido tu resultado?")
        )
    
    return (
        "✅ Vuelve a sumar las líneas parciales de abajo arriba, columna a columna. "
        "Comprueba bien las llevadas. Si no cuadra, revisa cada línea parcial."
    )

# ────────── Integración con OpenAI ──────────
try:
    from openai import OpenAI
    import os
    _client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    _USE_AI = bool(os.getenv("OPENAI_API_KEY"))
except Exception:
    _client = None
    _USE_AI = False

PROMPT = (
    "Eres Tutorín (profesor de Primaria, LOMLOE). Da pistas concisas (1–2 frases), "
    "amables y concretas para el PASO indicado. No cambies de paso. "
    "Si el alumno pregunta '¿por qué número empiezo?', aclara que se empieza por UNIDADES del número de abajo. "
    "Paso: {step} | Contexto: {context} | Respuesta: {answer} | Errores: {err}"
)

def _ai_hint(step: str, context: str, answer: str, err: int) -> Optional[str]:
    """Genera pista usando OpenAI si está disponible y err >= 2."""
    if not _USE_AI or not _client or err < 2:
        return None
    
    try:
        res = _client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": "Eres un profesor de Primaria empático, claro y paciente."},
                {"role": "user", "content": PROMPT.format(step=step, context=context, answer=answer, err=err)},
            ],
            temperature=0.4,
            max_tokens=120,
        )
        from .hints_utils import _sanitize
        txt = (res.choices[0].message.content or "").strip()
        return txt
    except Exception:
        return None

# ────────── Función principal (API pública) ──────────
def get_hint(hint_type: str, errors: int = 0, context: str = "", answer: str = "") -> str:
    """
    Genera pista para multiplicación según hint_type y nivel de error.
    
    Args:
        hint_type: 'mult_parcial' o 'mult_total'
        errors: nivel de error (0-4+)
        context: contexto del motor
        answer: respuesta del alumno
    """
    ec = max(1, min(int(errors or 1), 4))
    
    # Intentar con IA si err >= 2
    ai = _ai_hint(hint_type, context, answer, ec)
    if ai:
        return ai
    
    # Fallback a pistas locales
    if hint_type == "mult_parcial":
        return _mult_parcial_hint(context, ec, "c2")
    elif hint_type in ("mult_total", "mult_suma", "mult_resultado"):
        return _mult_suma_hint(context, ec, "c2")
    else:
        return "💡 Piensa paso a paso: multiplica por cada cifra del número de abajo y luego suma las líneas parciales."