
# -*- coding: utf-8 -*-
"""
multiplication_engine.py
Motor de multiplicación con pasos bien definidos:
- Líneas parciales (con desplazamiento implícito)
- Suma final de parciales
- hint_type coherente con hint_types.json
"""
import re
from typing import List

def _parse_mult(q: str):
    """Extrae dos enteros de una expresión como '123 * 45'."""
    q2 = q.replace("×", "*").replace("·", "*").replace("x", "*").replace("X", "*")
    m = re.search(r"^\s*(\d+)\s*\*\s*(\d+)\s*$", q2)
    if not m:
        return None
    a, b = int(m.group(1)), int(m.group(2))
    return a, b

def _compute_partials(a: int, b: int) -> List[int]:
    """Calcula las líneas parciales ya desplazadas (con ceros implícitos)."""
    parts = []
    b_str = str(b)[::-1]  # unidades primero
    for pos, ch in enumerate(b_str):
        d = int(ch)
        parts.append(a * d * (10 ** pos))  # incluye desplazamiento
    return parts

def _width(a: int, b: int) -> int:
    total = a * b
    return max(len(str(a)), len(str(b)) + 2, len(str(total))) + 2

def _board(a: int, b: int, partials: List[int], upto_index: int, show_sum_line: bool) -> str:
    """Genera el tablero visual de la multiplicación."""
    w = _width(a, b)
    rj = lambda s: s.rjust(w)
    lines = [
        rj(str(a)),
        rj("× " + str(b)),
        rj("-" * max(len(str(a)), len(str(b)) + 2))
    ]
    for i in range(upto_index):
        lines.append(rj(str(partials[i])))
    if show_sum_line and upto_index > 0:
        lines.append(rj("-" * max(len(str(p)) for p in partials[:upto_index])))
    return "<pre style='font-family:monospace;line-height:1.25;margin:6px 0 0 0'>" + "\n".join(lines) + "</pre>"

def handle_step(question: str, step_now: int, last_answer: str, error_count: int, cycle: str = "c2"):
    parsed = _parse_mult(question)
    if not parsed:
        return None
    a, b = parsed
    partials = _compute_partials(a, b)
    n = len(partials)

    # Paso 0 a n-1: líneas parciales
    if 0 <= step_now < n:
        digit_pos = step_now
        digit = int(str(b)[::-1][digit_pos])
        board = _board(a, b, partials, upto_index=step_now, show_sum_line=False)
        if step_now == 0:
            msg = (
                f"{board}"
                f"👉 Multiplica <b>{a}</b> por la cifra de <b>unidades</b> del número de abajo: <b>{digit}</b>. "
                "Escribe esa <b>línea parcial</b> (sin desplazar)."
            )
        else:
            place = ["unidades", "decenas", "centenas", "millares"][digit_pos] if digit_pos < 4 else f"posición {digit_pos}"
            msg = (
                f"{board}"
                f"👉 Multiplica <b>{a}</b> por la cifra de <b>{place}</b> del número de abajo: <b>{digit}</b>. "
                "Escribe la <b>línea parcial</b> (ya incluye los ceros por desplazamiento)."
            )
        return {
            "status": "ask",
            "message": msg,
            "expected_answer": str(partials[digit_pos]),
            "topic": "multiplicacion",
            "hint_type": "mult_parcial",
            "next_step": step_now + 1
        }

    # Paso n: suma de parciales
    if step_now == n:
        board = _board(a, b, partials, upto_index=n, show_sum_line=True)
        total = a * b
        return {
            "status": "ask",
            "message": (
                f"{board}"
                "👉 Ahora <b>suma en vertical</b> todas las líneas parciales para obtener el resultado final. "
                "Escribe solo el <b>resultado</b>."
            ),
            "expected_answer": str(total),
            "topic": "multiplicacion",
            "hint_type": "mult_suma",          # ✅ Corregido: coincide con hint_types.json
            "next_step": step_now + 1          # ✅ Añadido
        }

    # Paso final: completado
    if step_now > n:
        board = _board(a, b, partials, upto_index=n, show_sum_line=True)
        return {
            "status": "done",
            "message": f"{board}✅ ¡Buen trabajo! Has terminado la multiplicación.",
            "expected_answer": "ok",
            "topic": "multiplicacion",
            "hint_type": "mult_resultado",     # ✅ Opcional, pero válido
            "next_step": step_now + 1          # ✅ Añadido
        }

    # Fallback
    board = _board(a, b, partials, upto_index=0, show_sum_line=False)
    return {
        "status": "ask",
        "message": f"{board}Sigamos con la multiplicación.",
        "expected_answer": None,
        "topic": "multiplicacion",
        "hint_type": "mult_parcial",
        "next_step": step_now + 1
    }