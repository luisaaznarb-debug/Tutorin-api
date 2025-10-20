# -*- coding: utf-8 -*-
"""
ai_router.py
Sistema de pistas para Tutorin:
- Usa pistas internas por tipo de operación (suma, fracción, decimales, etc.)
- Si no hay pista definida, genera una con IA.
"""

import re
import os
from importlib import import_module

# === Importar validador de hint_types ===
from logic.core.hint_validator import is_valid_hint

# === Importar pistas internas ===
from .hints_addition import _sum_col_hint
from .hints_subtraction import _sub_col_hint
from .hints_multiplication import _mult_parcial_hint
from .hints_division import _division_hint
from .hints_fractions import (
    _frac_inicio_hint,
    _frac_mcm_hint,
    _frac_equiv_hint,
    _frac_operacion_hint,
    _frac_simplificar_hint,
)

# === IA opcional ===
try:
    from openai import OpenAI
    _client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    _USE_AI = bool(os.getenv("OPENAI_API_KEY"))
except Exception:
    _client = None
    _USE_AI = False


# === Función auxiliar para fracciones ===
def _ensure_frac_marker(ctx: str) -> str:
    """Reconstruye el marcador oculto de fracciones si falta."""
    text = ctx or ""
    if "[FRAC:" in text:
        return text

    m = re.search(r"(\d+)\s*/\s*(\d+)\s*([+\-])\s*(\d+)\s*/\s*(\d+)", text)
    if m:
        a, b, op, c, d = m.groups()
        return text + f"<span style='display:none'>[FRAC:{a}/{b}{op}{c}/{d}]</span>"
    return text


# === IA: generación de pista cuando no hay módulo ===
def _generate_ai_hint(prompt: str, step: str, error_count: int, context: str = "") -> str:
    """Genera una pista usando IA si no existe pista interna."""
    if not _USE_AI or not _client:
        return "Pista: piensa paso a paso, revisa el número y vuelve a intentarlo."

    try:
        sys_msg = (
            "Eres Tutorin, un profesor de Primaria en España. "
            "Da una pista breve, concreta y motivadora para ayudar al alumno "
            "a avanzar en su razonamiento sin resolverle todo."
        )
        user_msg = f"Consigna: {prompt}\nPaso: {step}\nErrores: {error_count}\nContexto: {context}"
        chat = _client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": sys_msg},
                {"role": "user", "content": user_msg},
            ],
            temperature=0.5,
        )
        return chat.choices[0].message.content.strip()
    except Exception as e:
        print(f"[AI_ROUTER] Error generando pista IA: {e}")
        return "No tengo una pista clara ahora mismo, intenta explicar cómo lo estás haciendo."


# === Generador principal de pistas ===
def generate_hint_with_ai(
    topic: str,
    step: str,
    question_or_context: str,
    answer: str = "",
    error_count: int = 1,
    cycle: str = "c2"
) -> str:
    """
    Genera una pista según el tema y el paso del ejercicio.
    - Usa pistas internas si existen.
    - Si no, intenta cargar el módulo hints_<topic>.
    - Si tampoco existe, usa IA como último recurso.
    """
    t = (topic or "").lower().strip()
    c = cycle or "c2"
    ctx = question_or_context or ""

    # Validar número de errores
    try:
        e = int(error_count)
    except Exception:
        e = 1
    e = max(1, min(e, 9))

    # --- Suma ---
    if t == "suma":
        hint = _sum_col_hint(ctx, e, c)
        _validate_hint_type(t, "add_col")
        return hint

    # --- Resta ---
    if t == "resta":
        hint = _sub_col_hint(ctx, e, c)
        _validate_hint_type(t, "sub_col")
        return hint

    # --- Multiplicación ---
    if t == "multiplicacion":
        hint = _mult_parcial_hint(ctx, e, c)
        _validate_hint_type(t, "mult_parcial")
        return hint

    # --- División ---
    if t == "division":
        hint = _division_hint(ctx, e, c)
        _validate_hint_type(t, "div_qdigit")
        return hint

    # --- Fracciones ---
    if t == "fracciones":
        ctx = _ensure_frac_marker(ctx)
        if step == "frac_inicio":
            _validate_hint_type(t, step)
            return _frac_inicio_hint(ctx, e, c)
        if step == "frac_mcm":
            _validate_hint_type(t, step)
            return _frac_mcm_hint(ctx, e, c)
        if step == "frac_equiv":
            _validate_hint_type(t, step)
            return _frac_equiv_hint(ctx, e, c)
        if step == "frac_operacion":
            _validate_hint_type(t, step)
            return _frac_operacion_hint(ctx, e, c)
        if step == "frac_simplificar":
            _validate_hint_type(t, step)
            return _frac_simplificar_hint(ctx, e, c)

    # --- Decimales ---
    if t == "decimales":
        try:
            from .hints_decimals import get_hint as _decimal_hint
            hint = _decimal_hint(step, e)
            _validate_hint_type(t, step)
            return hint
        except ModuleNotFoundError:
            pass
        except Exception as ex:
            print(f"[AI_ROUTER] Error al importar hints_decimals:", ex)

    # --- Carga dinámica genérica ---
    try:
        hints_module = import_module(f"logic.ai_hints.hints_{t}")
        if hasattr(hints_module, "get_hint"):
            hint = hints_module.get_hint(step, e)
            _validate_hint_type(t, step)
            return hint
    except ModuleNotFoundError:
        pass
    except Exception as ex:
        print(f"[AI_ROUTER] Error importando hints dinámicos ({t}):", ex)

    # --- Último recurso: IA ---
    hint = _generate_ai_hint(topic, step, e, ctx)
    _validate_hint_type("general", "ai_generated")
    return hint


# === VALIDACIÓN SILENCIOSA DE hint_types ===
def _validate_hint_type(topic: str, hint_type: str) -> None:
    """
    Valida silenciosamente si un hint_type es válido según hint_types.json.
    No interrumpe la ejecución, solo muestra advertencias en consola.
    """
    if not is_valid_hint(topic, hint_type):
        print(f"[AI_ROUTER] ⚠️ Hint_type desconocido '{hint_type}' para tema '{topic}'.")
