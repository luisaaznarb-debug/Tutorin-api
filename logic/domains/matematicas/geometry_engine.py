# -*- coding: utf-8 -*-
import re, math
from logic.ai_hints.ai_router import generate_hint_with_ai

# ──────────────────────────────────────────────
# Detección de figura y tipo de problema
# ──────────────────────────────────────────────

def _parse_geometry(question: str):
    q = question.lower().replace(",", ".")
    # Detectar figura
    if "cuadrado" in q:
        fig = "cuadrado"
    elif "rectángulo" in q or "rectangulo" in q:
        fig = "rectángulo"
    elif "triángulo" in q or "triangulo" in q:
        fig = "triángulo"
    elif "círculo" in q or "circulo" in q:
        fig = "círculo"
    else:
        return None

    # Detectar magnitud
    if "área" in q:
        tipo = "area"
    elif "perímetro" in q or "perimetro" in q:
        tipo = "perimetro"
    else:
        tipo = "area"  # por defecto

    # Detectar valores
    m = re.findall(r"(\d+(?:\.\d+)?)", q)
    nums = [float(n) for n in m]

    return fig, tipo, nums


# ──────────────────────────────────────────────
# Cálculos geométricos
# ──────────────────────────────────────────────

def _formula(fig: str, tipo: str):
    if fig == "cuadrado" and tipo == "perimetro":
        return "4 × lado"
    if fig == "cuadrado" and tipo == "area":
        return "lado × lado"
    if fig == "rectángulo" and tipo == "perimetro":
        return "2 × (base + altura)"
    if fig == "rectángulo" and tipo == "area":
        return "base × altura"
    if fig == "triángulo" and tipo == "area":
        return "base × altura ÷ 2"
    if fig == "círculo" and tipo == "area":
        return "π × radio²"
    if fig == "círculo" and tipo == "perimetro":
        return "2 × π × radio"
    return None


def _calculate(fig: str, tipo: str, nums):
    try:
        if fig == "cuadrado" and tipo == "perimetro":
            return 4 * nums[0]
        if fig == "cuadrado" and tipo == "area":
            return nums[0] ** 2
        if fig == "rectángulo" and tipo == "perimetro":
            return 2 * (nums[0] + nums[1])
        if fig == "rectángulo" and tipo == "area":
            return nums[0] * nums[1]
        if fig == "triángulo" and tipo == "area":
            return nums[0] * nums[1] / 2
        if fig == "círculo" and tipo == "area":
            return math.pi * (nums[0] ** 2)
        if fig == "círculo" and tipo == "perimetro":
            return 2 * math.pi * nums[0]
    except Exception:
        return None
    return None


# ──────────────────────────────────────────────
# Motor principal
# ──────────────────────────────────────────────

def handle_step(question: str, step_now: int, last_answer: str, error_count: int, cycle: str = "c2"):
    parsed = _parse_geometry(question)
    if not parsed:
        return None
    fig, tipo, nums = parsed
    formula = _formula(fig, tipo)

    # Paso 0 → reconocer figura y magnitud
    if step_now == 0:
        msg = (
            f"👉 Vamos a calcular el <b>{'área' if tipo=='area' else 'perímetro'}</b> "
            f"de un <b>{fig}</b>.<br/>"
            f"Primero recuerda la fórmula:<br/><b>{formula}</b>"
        )
        return {
            "status": "ask",
            "message": msg,
            "expected_answer": formula,
            "topic": "geometria",
            "hint_type": "geo_formula",
            "next_step": step_now + 1
        }

    # Paso 1 → sustituir valores
    if step_now == 1:
        if not nums:
            return {
                "status": "done",
                "message": "❌ No se encontraron valores numéricos en la consigna.",
                "expected_answer": "error",
                "topic": "geometria",
                "hint_type": "geo_missing",
                "next_step": step_now + 1
            }
        formula_filled = formula
        if fig == "cuadrado":
            formula_filled = formula.replace("lado", str(nums[0]))
        elif fig == "rectángulo":
            formula_filled = formula.replace("base", str(nums[0])).replace("altura", str(nums[1]))
        elif fig == "triángulo":
            formula_filled = formula.replace("base", str(nums[0])).replace("altura", str(nums[1]))
        elif fig == "círculo":
            formula_filled = formula.replace("radio", str(nums[0]))

        msg = (
            f"✅ Muy bien.<br/>Sustituyamos los valores en la fórmula:<br/>"
            f"<b>{formula_filled}</b>"
        )
        return {
            "status": "ask",
            "message": msg,
            "expected_answer": formula_filled,
            "topic": "geometria",
            "hint_type": "geo_substitute",
            "next_step": step_now + 1
        }

    # Paso 2 → cálculo numérico
    if step_now == 2:
        result = _calculate(fig, tipo, nums)
        if result is None:
            return {
                "status": "done",
                "message": "❌ No se pudo calcular el resultado.",
                "expected_answer": "error",
                "topic": "geometria",
                "hint_type": "geo_error",
                "next_step": step_now + 1
            }
        msg = (
            f"👉 Ahora realiza el cálculo numérico:<br/>"
            f"Resultado = <b>{round(result, 2)}</b>"
        )
        return {
            "status": "ask",
            "message": msg,
            "expected_answer": str(round(result, 2)),
            "topic": "geometria",
            "hint_type": "geo_calc",
            "next_step": step_now + 1
        }

    # Paso 3 → cierre
    if step_now == 3:
        result = _calculate(fig, tipo, nums)
        msg = (
            f"✅ ¡Excelente! 🎉<br/>"
            f"El <b>{'área' if tipo=='area' else 'perímetro'}</b> del <b>{fig}</b> es "
            f"<b>{round(result, 2)}</b> unidades."
        )
        return {
            "status": "done",
            "message": msg,
            "expected_answer": str(round(result, 2)),
            "topic": "geometria",
            "hint_type": "geo_result",
            "next_step": step_now + 1
        }

    # Seguridad
    return {
        "status": "done",
        "message": "✅ Has completado el ejercicio de geometría correctamente.",
        "expected_answer": "ok",
        "topic": "geometria",
        "hint_type": "geo_result",
        "next_step": step_now + 1
    }
