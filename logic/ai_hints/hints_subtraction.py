# -*- coding: utf-8 -*-
"""
hints_subtraction.py
Pistas progresivas para resta según nivel de error.
Compatible con subtraction_engine.py
"""

from .hints_utils import _extract_pre_block, _first_int_on_line, _question
import re
from typing import Optional

# ────────── Utilidades ──────────
def _parse_sub_from_context(ctx: str):
    """Extrae los dos números de una resta del contexto."""
    lines = _extract_pre_block(ctx).splitlines()
    if len(lines) < 2:
        return None
    a = _first_int_on_line(lines[0])
    b = _first_int_on_line(lines[1])
    if a is None or b is None:
        return None
    return (a, b)

def _explain_column_sub(a_digit: int, b_digit: int, borrowed: bool) -> str:
    """Explica la resta de una columna con préstamo."""
    if borrowed:
        actual_a = a_digit - 1
        if actual_a < b_digit:
            explanation = (
                f"{a_digit} - 1 (prestada) = {actual_a}. Como {actual_a} < {b_digit}, "
                f"pedimos prestada otra: {actual_a + 10} - {b_digit} = {actual_a + 10 - b_digit}"
            )
        else:
            explanation = f"{a_digit} - 1 (prestada) - {b_digit} = {actual_a - b_digit}"
    else:
        if a_digit < b_digit:
            explanation = (
                f"{a_digit} < {b_digit}, así que pedimos prestada 1 de la siguiente columna: "
                f"{a_digit + 10} - {b_digit} = {a_digit + 10 - b_digit}"
            )
        else:
            explanation = f"{a_digit} - {b_digit} = {a_digit - b_digit}"
    
    return explanation

# ────────── Pistas progresivas ──────────
def _sub_col_hint(context: str, err: int, cycle: str) -> str:
    """
    Pistas para restar una columna.
    Niveles:
    - 1: pista básica
    - 2: recordatorio con préstamo
    - 3: explicación paso a paso
    - 4+: casi-solución
    """
    parsed = _parse_sub_from_context(context)
    
    # Nivel 1: pista básica
    if err == 1:
        if parsed:
            a, b = parsed
            return (
                f"👉 Resta la cifra de abajo de la cifra de arriba en la columna de las <b>unidades</b>. "
                f"Si no puedes, pide prestada 1 de la siguiente columna. "
                + _question("¿Cuánto queda?")
            )
        return (
            "👉 Resta la cifra de abajo de la cifra de arriba. "
            "Si la de arriba es menor, pide prestada 1 de la izquierda. "
            + _question("¿Qué resultado obtienes?")
        )
    
    # Nivel 2: recordatorio con préstamo
    if err == 2:
        return (
            "🧮 Si pediste prestado, recuerda que equivale a <b>10 unidades</b>. "
            "Suma 10 a la cifra de arriba y luego resta. No olvides restar 1 de la siguiente columna. "
            + _question("¿Qué número queda?")
        )
    
    # Nivel 3: explicación paso a paso
    if err == 3:
        if parsed:
            a, b = parsed
            a_units = int(str(a)[-1])
            b_units = int(str(b)[-1])
            explanation = _explain_column_sub(a_units, b_units, False)
            return f"💡 Vamos paso a paso: {explanation}"
        return (
            "💡 Resta columna por columna de derecha a izquierda. "
            "Si una cifra de arriba es menor que la de abajo, pide prestada 10 de la siguiente columna. "
            + _question("¿Cuál es la diferencia?")
        )
    
    # Nivel 4+: casi-solución
    if err >= 4:
        if parsed:
            a, b = parsed
            result = a - b
            return f"✅ La resta completa es: {a} − {b} = <b>{result}</b>."
        return "✅ Revisa cada columna y escribe el resultado correcto."
    
    return "Resta columna por columna, pidiendo prestado si es necesario."

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
    "amables y concretas para restas. No reveles la solución completa. "
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
    Genera pista para resta según hint_type y nivel de error.
    
    Args:
        hint_type: 'sub_col', 'sub_resta', 'sub_resultado'
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
    return _sub_col_hint(context, ec, "c2")