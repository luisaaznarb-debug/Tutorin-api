# -*- coding: utf-8 -*-
"""
hints_percentages.py
Pistas progresivas para porcentajes según nivel de error.
Compatible con percentages_engine.py
"""

from typing import Optional

def get_hint(hint_type: str, errors: int = 0) -> str:
    """
    Devuelve una pista educativa según el tipo de paso y número de errores.
    
    Args:
        hint_type: tipo de paso del motor de porcentajes
        errors: nivel de error (0-4+)
    """
    errors = max(0, min(int(errors or 0), 4))

    # ────────── INTERPRETAR PORCENTAJE COMO FRACCIÓN ──────────
    if hint_type == "perc_frac" or hint_type == "percent_identificar":
        if errors == 0:
            return (
                "👉 Recuerda que <b>porcentaje</b> significa 'de cada 100'. "
                "Por ejemplo: 25% = 25/100."
            )
        elif errors == 1:
            return (
                "🧮 Convierte el número en una fracción con denominador 100. "
                "Por ejemplo: 30% = 30/100, 15% = 15/100."
            )
        elif errors == 2:
            return (
                "💡 El símbolo % significa 'por ciento', es decir, 'dividido entre 100'. "
                "Intenta escribirlo así: <b>porcentaje / 100</b>."
            )
        else:
            return (
                "✅ Ejemplo completo:\n"
                "25% = 25/100\n"
                "50% = 50/100 = 1/2\n"
                "75% = 75/100 = 3/4"
            )

    # ────────── MULTIPLICACIÓN POR LA CANTIDAD BASE ──────────
    if hint_type == "perc_mult" or hint_type == "percent_transformar":
        if errors == 0:
            return (
                "👉 Multiplica la fracción por la cantidad base. "
                "Por ejemplo: (25/100) × 80."
            )
        elif errors == 1:
            return (
                "🧮 El número después de 'de' es el que debes multiplicar. "
                "Por ejemplo: 25% de 80 = 80 × (25/100)."
            )
        elif errors == 2:
            return (
                "💡 Paso a paso:\n"
                "1. Convierte el porcentaje a fracción: 25% = 25/100\n"
                "2. Multiplica: 80 × 25 = 2000\n"
                "3. Divide entre 100: 2000/100 = 20"
            )
        else:
            return (
                "✅ Fórmula general:\n"
                "Porcentaje de una cantidad = (porcentaje/100) × cantidad\n"
                "Ejemplo: 30% de 50 = (30/100) × 50 = 15"
            )

    # ────────── SIMPLIFICAR EL RESULTADO ──────────
    if hint_type == "perc_simplify" or hint_type == "percent_calculo":
        if errors == 0:
            return (
                "👉 Divide entre 100 o mueve la coma dos lugares a la izquierda. "
                "Por ejemplo, 2500/100 = 25 o 80/100 = 0,8."
            )
        elif errors == 1:
            return (
                "🧮 Mira el número y quita los dos ceros del 100: es como dividir entre 100. "
                "2000/100 = 20."
            )
        elif errors == 2:
            return (
                "💡 Truco: mover la coma dos lugares a la izquierda es lo mismo que dividir entre 100. "
                "Ejemplo: 350 → 3,50 → 3,5."
            )
        else:
            return (
                "✅ Ejemplo completo:\n"
                "25% de 80:\n"
                "80 × 25 = 2000\n"
                "2000 ÷ 100 = 20\n"
                "Resultado: 20"
            )

    # ────────── RESULTADO FINAL ──────────
    if hint_type == "perc_result" or hint_type == "percent_resultado":
        if errors == 0:
            return (
                "👉 Vuelve a leer: el resultado indica cuántas partes de la cantidad base representa el porcentaje."
            )
        elif errors == 1:
            return (
                "🧮 Por ejemplo, el 25% de 80 es 20, porque 20 es una cuarta parte de 80."
            )
        elif errors == 2:
            return (
                "💡 Comprueba que el resultado tenga sentido:\n"
                "- 50% de algo debe ser la mitad\n"
                "- 25% debe ser la cuarta parte\n"
                "- 10% debe ser la décima parte"
            )
        else:
            return (
                "✅ ¡Muy bien! Así se interpreta un porcentaje en la vida real. "
                "Los descuentos, impuestos y estadísticas usan porcentajes."
            )

    # ────────── FALLBACK ──────────
    return (
        "🤔 No tengo una pista específica para este paso. "
        "Intenta volver a leer la pregunta con calma. Recuerda: % significa /100. 🌈"
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
    "Eres Tutorín (profesor de Primaria, LOMLOE). Da pistas concisas (1–2 frases) "
    "para porcentajes. No reveles la solución completa. "
    "Paso: {step} | Errores: {err}"
)
def _ai_hint(hint_type: str, err: int) -> Optional[str]:
    """Genera pista con OpenAI si err >= 2."""
    if not _USE_AI or not _client or err < 2:
        return None
    
    try:
        res = _client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": "Eres un profesor de Primaria empático y paciente."},
                {"role": "user", "content": PROMPT.format(step=hint_type, err=err)},
            ],
            temperature=0.4,
            max_tokens=120,
        )
        return (res.choices[0].message.content or "").strip()
    except Exception:
        return None