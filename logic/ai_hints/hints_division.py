# -*- coding: utf-8 -*-
"""
hints_division.py
Pistas progresivas para división según nivel de error.
Compatible con division_engine.py
"""

from .hints_utils import _extract_pre_block, _question
import re
from typing import Optional

# ────────── Utilidades ──────────
def _parse_div_from_context(ctx: str):
    """Extrae dividendo y divisor del contexto."""
    txt = _extract_pre_block(ctx)
    m = re.search(r"(\d+)\s*[÷/:]\s*(\d+)", txt)
    if m:
        return int(m.group(1)), int(m.group(2))
    return None

# ────────── Pistas por subpaso ──────────
def _div_grupo_hint(context: str, err: int, cycle: str) -> str:
    """Pistas para elegir el primer grupo del dividendo."""
    m = re.search(r"dividir entre <b>(\d+)</b>", context)
    d = int(m.group(1)) if m else None
    
    if err == 1:
        return (
            "👉 Elige el <b>primer grupo del dividendo</b> (empezando por la izquierda) "
            "que sea mayor o igual al divisor. " + _question("¿Qué número es?")
        )
    
    if err == 2 and d:
        return (
            f"🧮 Avanza desde la izquierda hasta formar un número ≥ {d}. "
            f"Ese será el primer grupo con el que empezamos a dividir. "
            + _question("¿Cuál es ese número?")
        )
    
    if err >= 3:
        return (
            "💡 Recuerda: el primer grupo es el prefijo más corto del dividendo "
            "que sea suficientemente grande para dividir. Toma las cifras de izquierda a derecha."
        )
    
    return "Toma el prefijo mínimo del dividendo que sea ≥ al divisor."

def _div_qdigit_hint(context: str, err: int, cycle: str) -> str:
    """Pistas para elegir la cifra del cociente."""
    m = re.search(r"cabe <b>(\d+)</b> en <b>(\d+)</b>", context)
    div = int(m.group(1)) if m else None
    grp = int(m.group(2)) if m else None
    
    if err == 1:
        return (
            "👉 Piensa: ¿cuántas veces cabe el divisor en este grupo sin pasarte? "
            "Esa es la cifra del cociente. " + _question("¿Qué cifra pones?")
        )
    
    if err == 2 and div and grp:
        k = max(1, grp // div)
        return (
            f"🧮 Prueba con {div}×{k}={div*k}. "
            f"Si {div*k} > {grp}, baja 1; si {div*k} < {grp}, puedes subir 1. "
            + _question("¿Cuál es la cifra correcta?")
        )
    
    if err >= 3 and div and grp:
        q = grp // div
        return (
            f"💡 La cifra correcta es <b>{q}</b>, porque {div}×{q}={div*q} ≤ {grp} "
            f"y {div}×{q+1}={div*(q+1)} > {grp}."
        )
    
    return "Usa la tabla del divisor y elige la cifra más alta que no se pase."

def _div_resta_hint(context: str, err: int, cycle: str) -> str:
    """Pistas para la resta."""
    if err == 1:
        return (
            "👉 Resta el producto al grupo: grupo − (divisor × cifra del cociente). "
            + _question("¿Qué resto obtienes?")
        )
    
    if err == 2:
        return (
            "🧮 Escribe la resta en vertical para no confundirte. "
            "Recuerda que el resto debe ser <b>menor</b> que el divisor. "
            + _question("¿Cuál es el resto?")
        )
    
    if err >= 3:
        return (
            "💡 Comprueba que el resto sea menor que el divisor. "
            "Si no lo es, significa que la cifra del cociente era demasiado pequeña. "
            "Ajusta la cifra del cociente y vuelve a restar."
        )
    
    return "Resta el producto y verifica que el resto < divisor."

def _div_bajar_hint(context: str, err: int, cycle: str) -> str:
    """Pistas para bajar la siguiente cifra."""
    if err == 1:
        return (
            "👉 Baja la siguiente cifra del dividendo y júntala con el resto. "
            + _question("¿Qué nuevo número obtienes?")
        )
    
    if err == 2:
        return (
            "🧮 Piensa el nuevo número como: resto×10 + cifra bajada. "
            "Ahora vuelve a decidir la siguiente cifra del cociente. "
            + _question("¿Cuál es el nuevo grupo?")
        )
    
    if err >= 3:
        return (
            "💡 Forma bien el nuevo número antes de elegir la siguiente cifra del cociente. "
            "Recuerda que es como si pegaras la cifra bajada al final del resto."
        )
    
    return "Baja la cifra y forma el nuevo número correctamente."

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
    "Eres Tutorín (profesor de Primaria, LOMLOE). Da pistas concisas (1–2 frases) "
    "para divisiones paso a paso. No reveles la solución completa. "
    "Paso: {step} | Contexto: {context} | Respuesta: {answer} | Errores: {err}"
)

def _ai_hint(step: str, context: str, answer: str, err: int) -> Optional[str]:
    """Genera pista con OpenAI si err >= 2."""
    if not _USE_AI or not _client or err < 2:
        return None
    
    try:
        res = _client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": "Eres un profesor de Primaria empático y paciente."},
                {"role": "user", "content": PROMPT.format(step=step, context=context, answer=answer, err=err)},
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
    Genera pista para división según hint_type y nivel de error.
    
    Args:
        hint_type: 'div_grupo', 'div_qdigit', 'div_resta', 'div_bajar', 'div_resultado'
        errors: nivel de error (0-4+)
        context: contexto del motor
        answer: respuesta del alumno
    """
    ec = max(1, min(int(errors or 1), 4))
    
    # Intentar con IA
    ai = _ai_hint(hint_type, context, answer, ec)
    if ai:
        return ai
    
    # Fallback local
    if hint_type == "div_grupo":
        return _div_grupo_hint(context, ec, "c2")
    elif hint_type == "div_qdigit":
        return _div_qdigit_hint(context, ec, "c2")
    elif hint_type == "div_resta":
        return _div_resta_hint(context, ec, "c2")
    elif hint_type == "div_bajar":
        return _div_bajar_hint(context, ec, "c2")
    else:
        return "💡 Vamos paso a paso: elige el grupo, calcula la cifra, resta, baja la siguiente cifra y repite."