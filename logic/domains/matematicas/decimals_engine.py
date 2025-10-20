# -*- coding: utf-8 -*-
"""
decimals_engine.py
--------------------------------------------------
Motor para operaciones con números decimales:
suma, resta, multiplicación y división.
Guía paso a paso con el formato oficial de Tutorín.
"""

import re
from typing import Dict, Any

# -------------------------------------------------------
# Helpers
# -------------------------------------------------------

def _canon(s: str) -> str:
    """Normaliza texto."""
    return str(s or "").strip().lower().replace(",", ".").replace(" ", "")

def _extract_numbers(expr: str):
    """Extrae números decimales y operador (+, -, ×, ÷)."""
    expr = expr.replace(",", ".")
    m = re.search(r"(\d+(?:\.\d+)?)\s*([+\-×x*/:])\s*(\d+(?:\.\d+)?)", expr)
    if not m:
        return None
    a, op, b = m.groups()
    op = "×" if op in ("x", "×", "*") else "÷" if op in ("/", ":") else op
    return float(a), op, float(b)

# -------------------------------------------------------
# Motor principal
# -------------------------------------------------------

def handle_step(prompt: str, step: int, answer: str, errors: int) -> Dict[str, Any]:
    """
    Maneja una operación con números decimales paso a paso.
    Compatible con el formato estándar de salida de Tutorín.
    """
    aop = _extract_numbers(prompt)
    if not aop:
        return {
            "status": "ask",
            "message": (
                "Necesito una operación con números decimales 😊.<br/>"
                "Ejemplo: <code>3,2 + 1,45</code> o <code>2,4 × 0,3</code>."
            ),
            "expected_answer": None,
            "topic": "decimales",
            "hint_type": "decimal_start",
            "next_step": 0,
        }

    a, op, b = aop
    html_expr = f"<b>{a:g} {op} {b:g}</b>"

    # ---------------------------------------------------
    # Paso 0 → identificar tipo de operación
    # ---------------------------------------------------
    if step == 0:
        msg = (
            f"Vamos a trabajar con <b>números decimales</b> ✨.<br/>"
            f"¿Qué tipo de operación es esta? (+, −, × o ÷)<br/>{html_expr}"
        )
        expected = op
        return {
            "status": "ask",
            "message": msg,
            "expected_answer": expected,
            "topic": "decimales",
            "hint_type": "decimal_identificar",
            "next_step": 1,
        }

    # ---------------------------------------------------
    # Paso 1 → alineación de comas
    # ---------------------------------------------------
    if step == 1:
        msg = (
            f"✅ ¡Muy bien! 😊 Ahora escribe los números **alineando las comas decimales**.<br/>"
            f"Por ejemplo:<br/><code>{a:g}</code><br/><code>{b:g}</code><br/>"
            f"¿Listo para operar?"
        )
        expected = "sí"
        return {
            "status": "ask",
            "message": msg,
            "expected_answer": expected,
            "topic": "decimales",
            "hint_type": "decimal_alinear",
            "next_step": 2,
        }

    # ---------------------------------------------------
    # Paso 2 → operación sin coma
    # ---------------------------------------------------
    if step == 2:
        msg = (
            f"Genial 👍. Si quitamos temporalmente la coma, "
            f"la operación sería con números enteros.<br/>"
            f"¿Cuánto da <b>{a * (10 ** 1):.0f} {op} {b * (10 ** 1):.0f}</b>?"
        )
        return {
            "status": "ask",
            "message": msg,
            "expected_answer": None,
            "topic": "decimales",
            "hint_type": "decimal_operar",
            "next_step": 3,
        }

    # ---------------------------------------------------
    # Paso 3 → recolocar coma en el resultado
    # ---------------------------------------------------
    if step == 3:
        result = None
        try:
            if op == "+":
                result = round(a + b, 3)
            elif op == "-":
                result = round(a - b, 3)
            elif op in ("×", "*"):
                result = round(a * b, 3)
            elif op in ("÷", "/"):
                result = round(a / b, 3) if b != 0 else "∞"
        except Exception:
            result = "error"

        msg = (
            f"✅ ¡Perfecto! 😊 Ahora vuelve a colocar la coma en su sitio correcto 😉.<br/>"
            f"El resultado es <b>{result}</b>."
        )
        return {
            "status": "done",
            "message": msg,
            "expected_answer": str(result),
            "topic": "decimales",
            "hint_type": "decimal_resultado",
            "next_step": 4,
        }

    # ---------------------------------------------------
    # Fallback
    # ---------------------------------------------------
    return {
        "status": "ask",
        "message": (
            f"🤔 No entiendo bien este paso.<br/>"
            f"Volvamos a revisar la operación: {html_expr}"
        ),
        "expected_answer": None,
        "topic": "decimales",
        "hint_type": "decimal_error",
        "next_step": 0,
    }
