# -*- coding: utf-8 -*-
"""
hints_geometry.py
Pistas progresivas para geometría según nivel de error.
Compatible con geometry_engine.py
"""

from typing import Optional

def get_hint(hint_type: str, errors: int = 0) -> str:
    """
    Devuelve una pista según el tipo de paso y el número de errores.
    
    Args:
        hint_type: tipo de paso del motor de geometría
        errors: nivel de error (0-4+)
    """
    errors = max(0, min(int(errors or 0), 4))
    
    # ────────── IDENTIFICAR FIGURA ──────────
    if hint_type == "geo_identificar":
        if errors == 0:
            return (
                "👉 Identifica qué figura geométrica tienes: "
                "¿es un <b>cuadrado</b>, <b>rectángulo</b>, <b>triángulo</b> o <b>círculo</b>?"
            )
        elif errors == 1:
            return (
                "🧮 Observa cuántos lados tiene la figura. "
                "Los cuadrados y rectángulos tienen 4 lados, los triángulos 3, y los círculos no tienen lados."
            )
        elif errors == 2:
            return (
                "💡 Piensa en las características:\n"
                "- Cuadrado: 4 lados iguales\n"
                "- Rectángulo: 4 lados, 2 pares iguales\n"
                "- Triángulo: 3 lados\n"
                "- Círculo: redondo, sin esquinas"
            )
        else:
            return (
                "✅ Mira el dibujo o la descripción con calma. "
                "Si tiene 4 lados iguales es un cuadrado, si tiene 4 lados con 2 parejas iguales es un rectángulo."
            )

    # ────────── RECORDAR FÓRMULA ──────────
    if hint_type == "geo_formula":
        if errors == 0:
            return (
                "👉 Piensa qué figura geométrica estás trabajando. "
                "Cada una tiene su fórmula propia para el área o perímetro."
            )
        elif errors == 1:
            return (
                "🧮 Ejemplos de fórmulas:\n"
                "- Cuadrado: lado × lado (área), 4 × lado (perímetro)\n"
                "- Triángulo: base × altura ÷ 2 (área)\n"
                "- Círculo: π × radio² (área)"
            )
        elif errors == 2:
            return (
                "💡 Si dudas, imagina dibujar la figura y recuerda cuántos lados o dimensiones tiene. "
                "El área mide el espacio dentro, el perímetro mide el borde."
            )
        else:
            return (
                "✅ Busca en tus apuntes o recuerda:\n"
                "- Rectángulo área = base × altura\n"
                "- Cuadrado área = lado × lado\n"
                "- Triángulo área = base × altura ÷ 2"
            )

    # ────────── SUSTITUIR VALORES ──────────
    if hint_type == "geo_substitute" or hint_type == "geo_sustituir":
        if errors == 0:
            return (
                "👉 Sustituye los valores que aparecen en el problema dentro de la fórmula. "
                "Por ejemplo: si base = 8 y altura = 5, entonces área = 8 × 5."
            )
        elif errors == 1:
            return (
                "🧮 Ten cuidado con el orden: primero base, luego altura o radio según la figura. "
                "Escribe la fórmula y pon los números en su lugar."
            )
        elif errors == 2:
            return (
                "💡 Ejemplo: si la fórmula es base × altura ÷ 2 y tienes base=6, altura=4, "
                "entonces escribes: 6 × 4 ÷ 2."
            )
        else:
            return (
                "✅ Reemplaza cada palabra de la fórmula (base, altura, lado, radio) "
                "por el número correspondiente del enunciado."
            )

    # ────────── REALIZAR CÁLCULO ──────────
    if hint_type == "geo_calc":
        if errors == 0:
            return (
                "👉 Multiplica o divide los números según la fórmula. Hazlo paso a paso. "
                "Recuerda usar el orden correcto de operaciones."
            )
        elif errors == 1:
            return (
                "🧮 Orden de operaciones: primero multiplicaciones y divisiones (de izquierda a derecha), "
                "luego sumas y restas."
            )
        elif errors == 2:
            return (
                "💡 Ejemplo: 6 × 4 ÷ 2 → primero 6 × 4 = 24, luego 24 ÷ 2 = 12."
            )
        else:
            return (
                "✅ Usa la calculadora si lo necesitas, pero asegúrate de seguir el orden correcto. "
                "Redondea el resultado si tiene muchos decimales."
            )

    # ────────── INTERPRETAR RESULTADO ──────────
    if hint_type == "geo_result" or hint_type == "geo_resultado":
        if errors == 0:
            return (
                "👉 Piensa qué representa el número: si es <b>área</b>, son unidades cuadradas (cm², m²...). "
                "Si es <b>perímetro</b>, representa la longitud del borde (cm, m...)."
            )
        elif errors == 1:
            return (
                "🧮 El área mide el espacio dentro de la figura (cuadrados). "
                "El perímetro mide el borde de la figura (línea)."
            )
        elif errors == 2:
            return (
                "💡 Revisa si el número tiene sentido con el tamaño de la figura. "
                "¿Es muy grande o muy pequeño?"
            )
        else:
            return (
                "✅ ¡Buen trabajo! Recuerda siempre poner las unidades correctas: "
                "cm² para áreas, cm para perímetros, etc."
            )

    # ────────── FALLBACK ──────────
    return (
        "🤔 No tengo una pista específica para este paso, pero recuerda: "
        "identifica la figura, usa la fórmula y calcula con calma. 📐"
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
    "para geometría. No reveles la solución completa. "
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