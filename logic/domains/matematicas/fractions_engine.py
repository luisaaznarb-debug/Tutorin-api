# -*- coding: utf-8 -*-
"""
fractions_engine.py
Motor de fracciones con avance de pasos, soporte para suma/resta y m.c.m.
Compatible con hints_fractions.py
"""

from fractions import Fraction
import re
from math import lcm

# ──────────────────────────────────────────────
# Utilidades
# ──────────────────────────────────────────────

def _parse_frac_with_op(expr: str):
    """
    Extrae dos fracciones y el operador (+ o -) desde una cadena como '2/3 + 1/4'.
    Devuelve (f1: Fraction, f2: Fraction, op: str) o None si falla.
    """
    expr = expr.replace(":", "/").replace("÷", "/").replace(",", ".").strip()
    
    # Buscar patrón: número/numero [espacios] (+ o -) [espacios] número/numero
    m = re.search(r"(\d+)\s*/\s*(\d+)\s*([+\-])\s*(\d+)\s*/\s*(\d+)", expr)
    if not m:
        return None
    
    a, b, op, c, d = map(int, [m.group(1), m.group(2), m.group(4), m.group(5)])
    op_char = m.group(3)
    
    f1 = Fraction(a, b)
    f2 = Fraction(c, d)
    return f1, f2, op_char


def _pretty_frac(fr: Fraction) -> str:
    """Devuelve la fracción en formato HTML visual (tipo escolar)."""
    return f"<div style='display:inline-block;text-align:center;'><div>{fr.numerator}</div><hr style='margin:2px 0;' /><div>{fr.denominator}</div></div>"


# ──────────────────────────────────────────────
# Motor principal
# ──────────────────────────────────────────────

def handle_step(question: str, step_now: int, last_answer: str, error_count: int, cycle: str = "c2"):
    parsed = _parse_frac_with_op(question)
    if not parsed:
        return {
            "status": "error",
            "message": "⚠️ No pude entender la operación. Por favor escribe algo como: <b>2/3 + 1/4</b>.",
            "topic": "fracciones",
            "hint_type": "frac_inicio",
            "next_step": step_now
        }
    
    f1, f2, op = parsed
    op_symbol = " + " if op == "+" else " - "

    # Generar marcador oculto para las pistas
    hidden_marker = f"<span style='display:none'>[FRAC:{f1.numerator}/{f1.denominator}{op}{f2.numerator}/{f2.denominator}]</span>"

    # Paso 0: ¿Tienen el mismo denominador?
    if step_now == 0:
        same_den = f1.denominator == f2.denominator
        expected = "sí" if same_den else "no"
        msg = (
            f"👉 Observa las fracciones: {_pretty_frac(f1)} y {_pretty_frac(f2)}.<br/>"
            f"¿Tienen el mismo denominador (<b>{f1.denominator}</b> y <b>{f2.denominator}</b>)?"
            f"{hidden_marker}"
        )
        return {
            "status": "ask",
            "message": msg,
            "expected_answer": expected,
            "topic": "fracciones",
            "hint_type": "frac_inicio",
            "next_step": 1
        }

    # Paso 1: Calcular el m.c.m. (denominador común)
    if step_now == 1:
        common_den = lcm(f1.denominator, f2.denominator)
        msg = (
            f"👉 Calcula el <b>mínimo común múltiplo (m.c.m.)</b> de {f1.denominator} y {f2.denominator}.<br/>"
            f"Este será el nuevo denominador común."
            f"{hidden_marker}"
        )
        return {
            "status": "ask",
            "message": msg,
            "expected_answer": str(common_den),
            "topic": "fracciones",
            "hint_type": "frac_mcm",
            "next_step": 2
        }

    # Paso 2: Calcular fracciones equivalentes (nuevos numeradores)
    if step_now == 2:
        common_den = lcm(f1.denominator, f2.denominator)
        factor1 = common_den // f1.denominator
        factor2 = common_den // f2.denominator
        new_num1 = f1.numerator * factor1
        new_num2 = f2.numerator * factor2
        
        msg = (
            f"👉 Convierte ambas fracciones a denominador {common_den}:<br/>"
            f"{f1.numerator}/{f1.denominator} → <b>{new_num1}/{common_den}</b><br/>"
            f"{f2.numerator}/{f2.denominator} → <b>{new_num2}/{common_den}</b><br/>"
            f"Escribe los nuevos numeradores: <b>{new_num1} y {new_num2}</b>."
            f"{hidden_marker}"
        )
        return {
            "status": "ask",
            "message": msg,
            "expected_answer": f"{new_num1} y {new_num2}",
            "topic": "fracciones",
            "hint_type": "frac_equiv",
            "next_step": 3
        }

    # Paso 3: Operar los numeradores
    if step_now == 3:
        common_den = lcm(f1.denominator, f2.denominator)
        factor1 = common_den // f1.denominator
        factor2 = common_den // f2.denominator
        new_num1 = f1.numerator * factor1
        new_num2 = f2.numerator * factor2
        result_num = new_num1 + new_num2 if op == "+" else new_num1 - new_num2
        
        msg = (
            f"👉 Ahora {('suma' if op == '+' else 'resta')} los numeradores:<br/>"
            f"{new_num1} {op} {new_num2} = <b>{result_num}</b>.<br/>"
            f"Escribe la fracción resultante: <b>{result_num}/{common_den}</b>."
            f"{hidden_marker}"
        )
        return {
            "status": "ask",
            "message": msg,
            "expected_answer": f"{result_num}/{common_den}",
            "topic": "fracciones",
            "hint_type": "frac_operacion",
            "next_step": 4
        }

    # Paso 4: Simplificar la fracción
    if step_now == 4:
        common_den = lcm(f1.denominator, f2.denominator)
        factor1 = common_den // f1.denominator
        factor2 = common_den // f2.denominator
        new_num1 = f1.numerator * factor1
        new_num2 = f2.numerator * factor2
        result_num = new_num1 + new_num2 if op == "+" else new_num1 - new_num2
        
        unsimplified = Fraction(result_num, common_den)
        msg = (
            f"👉 La fracción que obtuviste es {result_num}/{common_den}.<br/>"
            f"Ahora <b>simplifícala</b> al máximo."
            f"{hidden_marker}"
        )
        return {
            "status": "ask",
            "message": msg,
            "expected_answer": str(unsimplified),
            "topic": "fracciones",
            "hint_type": "frac_simplificar",
            "next_step": 5
        }

    # Paso 5: ¡Éxito!
    if step_now == 5:
        result = f1 + f2 if op == "+" else f1 - f2
        msg = (
            f"✅ ¡Muy bien! 🎉<br/>"
            f"La respuesta final de {_pretty_frac(f1)} {op_symbol} {_pretty_frac(f2)} "
            f"es {_pretty_frac(result)}<br/>"
            f"(<b>{result}</b>)."
            f"{hidden_marker}"
        )
        return {
            "status": "done",
            "message": msg,
            "expected_answer": str(result),
            "topic": "fracciones",
            "hint_type": "frac_simplificar",
            "next_step": 6
        }

    # Fallback
    return {
        "status": "done",
        "message": "✅ ¡Has terminado la actividad!",
        "expected_answer": "ok",
        "topic": "fracciones",
        "hint_type": "frac_simplificar",
        "next_step": step_now + 1
    }