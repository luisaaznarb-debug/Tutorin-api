# -*- coding: utf-8 -*-
import re
from logic.ai_hints.ai_router import generate_hint_with_ai

# ──────────────────────────────────────────────────────────────
# Diccionario de equivalencias básicas
# ──────────────────────────────────────────────────────────────
_CONVERSIONS = {
    # Longitud
    "km": {"m": 1000, "cm": 100000, "mm": 1000000},
    "m": {"km": 1/1000, "cm": 100, "mm": 1000},
    "cm": {"m": 1/100, "mm": 10},
    "mm": {"m": 1/1000, "cm": 1/10},
    # Masa
    "kg": {"g": 1000, "mg": 1000000},
    "g": {"kg": 1/1000, "mg": 1000},
    "mg": {"g": 1/1000, "kg": 1/1000000},
    # Capacidad
    "l": {"ml": 1000, "cl": 100, "dl": 10},
    "ml": {"l": 1/1000, "cl": 1/10},
    "cl": {"l": 1/100, "ml": 10},
    "dl": {"l": 1/10, "ml": 100}
}

# ──────────────────────────────────────────────────────────────
# Funciones auxiliares
# ──────────────────────────────────────────────────────────────

def _parse_conversion(question: str):
    """
    Detecta expresiones tipo '3 km a m' o '2500 ml a l'.
    Devuelve (valor, unidad_origen, unidad_destino)
    """
    q = question.lower().replace(",", ".")
    m = re.search(r"(\d+(?:\.\d+)?)\s*([a-z]+)\s*(a|to)\s*([a-z]+)", q)
    if not m:
        return None
    value = float(m.group(1))
    from_unit = m.group(2)
    to_unit = m.group(4)
    return value, from_unit, to_unit


def _find_factor(from_unit: str, to_unit: str):
    """Busca el factor de conversión directo si existe."""
    if from_unit in _CONVERSIONS and to_unit in _CONVERSIONS[from_unit]:
        return _CONVERSIONS[from_unit][to_unit]
    return None


# ──────────────────────────────────────────────────────────────
# Motor principal
# ──────────────────────────────────────────────────────────────

def handle_step(question: str, step_now: int, last_answer: str, error_count: int, cycle: str = "c2"):
    parsed = _parse_conversion(question)
    if not parsed:
        return None
    value, from_unit, to_unit = parsed

    factor = _find_factor(from_unit, to_unit)
    if factor is None:
        return {
            "status": "done",
            "message": f"❌ No conozco la conversión entre <b>{from_unit}</b> y <b>{to_unit}</b> todavía.",
            "expected_answer": "error",
            "topic": "medidas",
            "hint_type": "meas_unknown",
            "next_step": step_now + 1
        }

    # Paso 0 → Identificar magnitud y tipo de conversión
    if step_now == 0:
        msg = (
            f"👉 Vamos a convertir <b>{value} {from_unit}</b> a <b>{to_unit}</b>.<br/>"
            "Primero identifiquemos si hay que multiplicar o dividir según la tabla de unidades.<br/>"
            "¿Crees que el número final será mayor o menor?"
        )
        return {
            "status": "ask",
            "message": msg,
            "expected_answer": "mayor" if factor > 1 else "menor",
            "topic": "medidas",
            "hint_type": "meas_estimate",
            "next_step": step_now + 1
        }

    # Paso 1 → Explicar el factor de conversión
    if step_now == 1:
        msg = (
            f"✅ Correcto.<br/>Entre <b>{from_unit}</b> y <b>{to_unit}</b> el factor es "
            f"<b>{factor}</b>.<br/>"
            f"Entonces debemos {'multiplicar' if factor > 1 else 'dividir'} "
            f"por {factor}."
        )
        return {
            "status": "ask",
            "message": msg,
            "expected_answer": f"{factor}",
            "topic": "medidas",
            "hint_type": "meas_factor",
            "next_step": step_now + 1
        }

    # Paso 2 → Realizar el cálculo
    if step_now == 2:
        result = round(value * factor, 4)
        msg = (
            f"👉 Ahora haz la operación:<br/>"
            f"{value} × {factor} = <b>{result}</b>.<br/>"
            f"Este es el valor en <b>{to_unit}</b> antes de redondear."
        )
        return {
            "status": "ask",
            "message": msg,
            "expected_answer": str(result),
            "topic": "medidas",
            "hint_type": "meas_calc",
            "next_step": step_now + 1
        }

    # Paso 3 → Cierre y refuerzo
    if step_now == 3:
        result = round(value * factor, 2)
        msg = (
            f"✅ ¡Muy bien hecho! 🎉<br/>"
            f"<b>{value} {from_unit}</b> equivalen a "
            f"<b>{result} {to_unit}</b>.<br/>"
            f"Has usado correctamente el factor de conversión {factor}."
        )
        return {
            "status": "done",
            "message": msg,
            "expected_answer": str(result),
            "topic": "medidas",
            "hint_type": "meas_result",
            "next_step": step_now + 1
        }

    # Seguridad
    return {
        "status": "done",
        "message": "✅ Conversión completada correctamente.",
        "expected_answer": "ok",
        "topic": "medidas",
        "hint_type": "meas_result",
        "next_step": step_now + 1
    }
