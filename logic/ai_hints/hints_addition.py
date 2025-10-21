# -*- coding: utf-8 -*-
"""
hints_addition.py
Pistas progresivas para suma según nivel de error.
Compatible con addition_engine.py
"""

from .hints_utils import _extract_pre_block, _first_int_on_line, _question
import re
from typing import Optional

# ────────── Utilidades ──────────
def _parse_sum_from_context(ctx: str):
    """Extrae los dos números de una suma del contexto."""
    lines = _extract_pre_block(ctx).splitlines()
    if len(lines) < 2:
        return None
    a = _first_int_on_line(lines[0])
    b = _first_int_on_line(lines[1])
    if a is None or b is None:
        return None
    return (a, b)

def _explain_column_sum(a_digit: int, b_digit: int, carry: int) -> str:
    """Explica la suma de una columna con llevada."""
    total = a_digit + b_digit + carry
    write = total % 10
    new_carry = total // 10
    
    if carry > 0:
        explanation = f"{a_digit} + {b_digit} + {carry} (llevada) = {total}"
    else:
        explanation = f"{a_digit} + {b_digit} = {total}"
    
    if new_carry > 0:
        explanation += f" → escribe <b>{write}</b> y llevas <b>{new_carry}</b>"
    else:
        explanation += f" → escribe <b>{write}</b>"
    
    return explanation

# ────────── Pistas progresivas ──────────
def _sum_col_hint(context: str, err: int, cycle: str) -> str:
    """
    Pistas para sumar una columna.
    Niveles:
    - 1: pista básica
    - 2: recordatorio con llevadas
    - 3: explicación paso a paso
    - 4+: casi-solución
    """
    parsed = _parse_sum_from_context(context)
    
    # Nivel 1: pista básica
    if err == 1:
        if parsed:
            a, b = parsed
            return (
                f"👉 Suma las cifras de las <b>unidades</b>: toma la última cifra de {a} "
                f"y la última cifra de {b}. " + _question("¿Cuánto te da?")
            )
        return (
            "👉 Suma las cifras de la columna de la derecha (unidades). "
            + _question("¿Qué resultado obtienes?")
        )
    
    # Nivel 2: recordatorio con llevadas
    if err == 2:
        return (
            "🧮 Si la suma de la columna pasa de 9, escribe solo la cifra de las unidades "
            "y <b>lleva 1</b> a la siguiente columna (a la izquierda). "
            + _question("¿Qué cifra escribes abajo?")
        )
    
    # Nivel 3: explicación paso a paso
    if err == 3:
        if parsed:
            a, b = parsed
            # Extraer últimas cifras
            a_units = int(str(a)[-1])
            b_units = int(str(b)[-1])
            explanation = _explain_column_sum(a_units, b_units, 0)
            return f"💡 Vamos paso a paso: {explanation}"
        return (
            "💡 Suma cifra a cifra de derecha a izquierda. "
            "Si una columna da 10 o más, escribe solo las unidades y lleva 1. "
            + _question("¿Cuál es el resultado de esta columna?")
        )
    
    # Nivel 4+: casi-solución
    if err >= 4:
        if parsed:
            a, b = parsed
            result = a + b
            return f"✅ La suma completa es: {a} + {b} = <b>{result}</b>."
        return "✅ Revisa cada columna y escribe el resultado correcto."
    
    return "Suma columna por columna de derecha a izquierda."

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
    "amables y concretas para sumas. No reveles la solución completa. "
    "Contexto: {context} | Respuesta: {answer} | Errores: {err}"
)

def _ai_hint(context: str, answer: str, err: int) -> Optional[str]:
    """Genera pista usando OpenAI si está disponible y err >= 2."""
    if not _USE_AI or not _client or err < 2:
        return None
    
    try:
        res = _client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": "Eres un profesor de Primaria empático, claro y paciente."},
                {"role": "user", "content": PROMPT.format(context=context, answer=answer, err=err)},
            ],
            temperature=0.4,
            max_tokens=120,
        )
        return (res.choices[0].message.content or "").strip()
    except Exception:
        return None

# ────────── Función principal (API pública) ──────────
def get_hint(hint_type: str, errors: int = 0, context: str = "", answer: str = "") -> str:
    """
    Genera pista para suma según hint_type y nivel de error.
    
    Args:
        hint_type: 'add_col', 'add_carry', 'add_resultado'
        errors: nivel de error (0-4+)
        context: contexto del motor
        answer: respuesta del alumno
    """
    ec = max(1, min(int(errors or 1), 4))
    
    # Intentar con IA si err >= 2
    ai = _ai_hint(context, answer, ec)
    if ai:
        return ai
    
    # Fallback a pistas locales
    return _sum_col_hint(context, ec, "c2")