# -*- coding: utf-8 -*-
"""
fractions_engine.py
Motor de fracciones con avance de pasos CORREGIDO
"""

from fractions import Fraction
import re
from logic.ai_hints.ai_router import generate_hint_with_ai

# ──────────────────────────────────────────────
# Utilidades de fracciones
# ──────────────────────────────────────────────

def _parse_frac(expr: str):
    """Detecta y devuelve dos fracciones a partir de una cadena tipo '3/4 + 5/6'."""
    expr = expr.replace(":", "/").replace("÷", "/").replace(",", ".")
    m = re.findall(r"(\d+)\s*/\s*(\d+)", expr)
    if len(m) >= 2:
        f1 = Fraction(int(m[0][0]), int(m[0][1]))
        f2 = Fraction(int(m[1][0]), int(m[1][1]))
        return f1, f2
    return None


def _pretty_frac(fr: Fraction) -> str:
    """Devuelve la fracción en formato HTML."""
    return f"<div style='display:inline-block;text-align:center;'><div>{fr.numerator}</div><hr style='margin:2px 0;' /><div>{fr.denominator}</div></div>"


def _canon(s: str) -> str:
    """Normaliza texto para comparación."""
    return str(s or "").strip().lower().replace(" ", "")


# ──────────────────────────────────────────────
# Motor principal
# ──────────────────────────────────────────────

def handle_step(question: str, step_now: int, last_answer: str, error_count: int, cycle: str = "c2"):
    parsed = _parse_frac(question)
    if not parsed:
        return None
    f1, f2 = parsed

    # Paso 0 → preguntar si tienen el mismo denominador
    if step_now == 0:
        msg = (
            f"👉 Observa las fracciones: {_pretty_frac(f1)} y {_pretty_frac(f2)}.<br/>"
            f"¿Tienen el mismo denominador (<b>{f1.denominator}</b> y <b>{f2.denominator}</b>)?"
        )
        
        # ✅ Determinar la respuesta correcta
        if f1.denominator == f2.denominator:
            expected = "sí"
        else:
            expected = "no"
        
        return {
            "status": "ask",
            "message": msg,
            "expected_answer": expected,
            "topic": "fracciones",
            "hint_type": "frac_intro",
            "next_step": 1  # ✅ IMPORTANTE: siguiente paso es 1
        }

    # Paso 1 → calcular denominador común
    if step_now == 1:
        common_den = f1.denominator * f2.denominator
        msg = (
            f"👉 Calcula el denominador común:<br/>"
            f"{f1.denominator} × {f2.denominator} = <b>{common_den}</b>."
        )
        return {
            "status": "ask",
            "message": msg,
            "expected_answer": str(common_den),
            "topic": "fracciones",
            "hint_type": "frac_den",
            "next_step": 2  # ✅ Siguiente paso
        }

    # Paso 2 → ajustar numeradores
    if step_now == 2:
        n1 = f1.numerator * f2.denominator
        n2 = f2.numerator * f1.denominator
        msg = (
            f"👉 Ajusta los numeradores al nuevo denominador común:<br/>"
            f"{f1.numerator}×{f2.denominator} = <b>{n1}</b> y "
            f"{f2.numerator}×{f1.denominator} = <b>{n2}</b>."
        )
        
        # Aceptar varias formas de respuesta
        expected_variants = [
            f"{n1} y {n2}",
            f"{n1}y{n2}",
            f"{n1},{n2}",
            f"{n1} {n2}"
        ]
        
        return {
            "status": "ask",
            "message": msg,
            "expected_answer": f"{n1} y {n2}",
            "topic": "fracciones",
            "hint_type": "frac_num",
            "next_step": 3  # ✅ Siguiente paso
        }

    # Paso 3 → suma de numeradores
    if step_now == 3:
        n1 = f1.numerator * f2.denominator
        n2 = f2.numerator * f1.denominator
        den = f1.denominator * f2.denominator
        suma = n1 + n2
        msg = (
            f"👉 Ahora suma los numeradores obtenidos:<br/>"
            f"{n1} + {n2} = <b>{suma}</b>.<br/>"
            f"Escribe la fracción resultante: <b>{suma}/{den}</b>."
        )
        return {
            "status": "ask",
            "message": msg,
            "expected_answer": f"{suma}/{den}",
            "topic": "fracciones",
            "hint_type": "frac_sum",
            "next_step": 4  # ✅ Siguiente paso
        }

    # Paso 4 → simplificar resultado y cierre
    if step_now == 4:
        result = f1 + f2
        msg = (
            f"✅ ¡Muy bien! 🎉<br/>"
            f"La fracción resultante simplificada es {_pretty_frac(result)} "
            f"(<b>{result}</b> en número mixto si corresponde)."
        )
        return {
            "status": "done",  # ✅ Marca fin
            "message": msg,
            "expected_answer": str(result),
            "topic": "fracciones",
            "hint_type": "frac_result",
            "next_step": 5  # ✅ Paso final
        }

    # Seguridad: si se pasa de pasos
    return {
        "status": "done",
        "message": "✅ Has completado correctamente la operación con fracciones.",
        "expected_answer": "ok",
        "topic": "fracciones",
        "hint_type": "frac_result",
        "next_step": step_now + 1
    }
