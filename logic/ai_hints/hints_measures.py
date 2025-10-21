# -*- coding: utf-8 -*-
"""
hints_measures.py
Pistas progresivas para medidas y unidades según nivel de error.
Compatible con measures_engine.py
"""

from typing import Optional

def get_hint(hint_type: str, errors: int = 0) -> str:
    """
    Devuelve una pista educativa según el tipo de paso y número de errores.
    
    Args:
        hint_type: tipo de paso del motor de medidas
        errors: nivel de error (0-4+)
    """
    errors = max(0, min(int(errors or 0), 4))

    # ────────── ESTIMAR SI AUMENTA O DISMINUYE ──────────
    if hint_type == "meas_estimate":
        if errors == 0:
            return (
                "👉 Piensa si la unidad nueva es <b>más pequeña o más grande</b> que la original. "
                "Eso te dirá si el número aumentará o disminuirá."
            )
        elif errors == 1:
            return (
                "🧮 Si pasas de kilómetros a metros, hay <b>más</b> unidades (porque el metro es más pequeño), "
                "así que el número será <b>mayor</b>."
            )
        elif errors == 2:
            return (
                "💡 Regla general:\n"
                "- Unidad más pequeña → número más grande\n"
                "- Unidad más grande → número más pequeño"
            )
        else:
            return (
                "✅ Ejemplo: 3 km = 3000 m (más unidades porque el metro es más pequeño). "
                "2500 ml = 2,5 l (menos unidades porque el litro es más grande)."
            )

    # ────────── RECORDAR EL FACTOR DE CONVERSIÓN ──────────
    if hint_type == "meas_factor":
        if errors == 0:
            return (
                "👉 Cada salto en la tabla de unidades multiplica o divide por 10, 100 o 1000. "
                "Por ejemplo: 1 km = 1000 m, 1 m = 100 cm, 1 l = 1000 ml."
            )
        elif errors == 1:
            return (
                "🧮 Busca el factor en la tabla de conversión:\n"
                "- km → m: ×1000\n"
                "- m → km: ÷1000\n"
                "- m → cm: ×100"
            )
        elif errors == 2:
            return (
                "💡 Si no recuerdas el factor, piensa cuántos ceros hay entre las dos unidades. "
                "Por ejemplo: de km a m hay 3 ceros (1000)."
            )
        else:
            return (
                "✅ Tabla de referencia:\n"
                "Longitud: km → m (×1000), m → cm (×100)\n"
                "Masa: kg → g (×1000)\n"
                "Capacidad: l → ml (×1000)"
            )

    # ────────── REALIZAR EL CÁLCULO ──────────
    if hint_type == "meas_calc":
        if errors == 0:
            return (
                "👉 Multiplica o divide según la dirección del cambio. "
                "Si cambias a una unidad más pequeña, <b>multiplica</b>; "
                "si es más grande, <b>divide</b>."
            )
        elif errors == 1:
            return (
                "🧮 Ejemplo: 3 km → m → 3 × 1000 = 3000 m. "
                "O al revés: 2500 ml → l → 2500 ÷ 1000 = 2,5 l."
            )
        elif errors == 2:
            return (
                "💡 Recuerda:\n"
                "- A unidad más pequeña: multiplicas (más unidades)\n"
                "- A unidad más grande: divides (menos unidades)"
            )
        else:
            return (
                "✅ Hazlo paso a paso con la calculadora si lo necesitas. "
                "Comprueba que el resultado tenga sentido con tu estimación inicial."
            )

    # ────────── INTERPRETAR EL RESULTADO FINAL ──────────
    if hint_type == "meas_result" or hint_type == "meas_resultado":
        if errors == 0:
            return (
                "👉 Revisa si el resultado tiene sentido: ¿es lógico que aumente o disminuya? "
                "Compara con tu estimación inicial."
            )
        elif errors == 1:
            return (
                "🧮 Ejemplo: 2500 ml son 2,5 litros. "
                "Tiene sentido porque el litro es una unidad más grande, así que hay menos litros."
            )
        elif errors == 2:
            return (
                "💡 Si convertiste correctamente, el resultado debe coincidir con tu predicción: "
                "número mayor si la unidad es más pequeña, número menor si la unidad es más grande."
            )
        else:
            return (
                "✅ ¡Muy bien! Ya dominas las equivalencias entre unidades. "
                "Practica con diferentes ejemplos para afianzar."
            )

    # ────────── UNIDAD DESCONOCIDA ──────────
    if hint_type == "meas_unknown":
        return (
            "😅 No reconozco esa conversión todavía. "
            "Asegúrate de usar unidades del Sistema Internacional (km, m, cm, kg, g, l, ml...)."
        )

    # ────────── FALLBACK ──────────
    return (
        "🤔 No tengo una pista específica para este paso, "
        "pero recuerda usar la tabla de unidades para orientarte. 📏"
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
    "para conversiones de medidas. No reveles la solución completa. "
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