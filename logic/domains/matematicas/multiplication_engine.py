# -*- coding: utf-8 -*-
import re
from typing import List, Dict, Tuple
from logic.ai_hints.ai_router import generate_hint_with_ai

# ──────────────────────────────────────────────────────────────
# Utilidades básicas
# ──────────────────────────────────────────────────────────────

_PLACES = [
    "unidades", "decenas", "centenas", "millares",
    "decenas de millar", "centenas de millar", "millones"
]

def _place_name(k: int) -> str:
    return _PLACES[k] if k < len(_PLACES) else f"posición {k}"

def _normalize(expr: str) -> str:
    return (
        expr.replace("×", "*")
            .replace("·", "*")
            .replace("x", "*")
            .replace("–", "-")
            .replace("−", "-")
    )

def _parse_mul(q: str) -> Tuple[int, int] | None:
    q = _normalize(q)
    m = re.search(r"(\d+)\s*\*\s*(\d+)", q)
    if not m:
        return None
    return int(m.group(1)), int(m.group(2))

def _digits_rev(n: int) -> List[int]:
    return [int(ch) for ch in str(n)][::-1]

def _board(a: int, b: int, solved_lines: List[str], show_total: bool = False) -> str:
    """Genera la representación visual de la multiplicación."""
    w = max(len(str(a)), len(str(b)) + 2, len(str(a * b))) + 2
    rj = lambda s: s.rjust(w)
    lines = [rj(str(a)), rj("× " + str(b)), rj("-" * max(len(str(a)), len(str(b)) + 2))]
    lines += [rj(line) for line in solved_lines]
    if show_total:
        lines.append(rj("-" * max(len(str(a)), len(str(b)) + 2)))
        lines.append(rj(str(a * b)))
    return (
        "<pre style='font-family:monospace;line-height:1.25;margin:6px 0 0 0'>"
        + "\n".join(lines)
        + "</pre>"
    )

# ──────────────────────────────────────────────────────────────
# Motor principal
# ──────────────────────────────────────────────────────────────

def handle_step(question: str, step_now: int, last_answer: str, error_count: int, cycle: str = "c2"):
    parsed = _parse_mul(question)
    if not parsed:
        return None
    a, b = parsed
    A = _digits_rev(a)
    B = _digits_rev(b)
    n, m = len(A), len(B)

    # Pasos intermedios ya resueltos
    solved_lines = []
    for i in range(min(step_now, m)):
        parcial = a * B[i]
        solved_lines.append(str(parcial) + " " * i)

    # Paso actual: multiplicación por cada dígito del multiplicador
    if 0 <= step_now < m:
        factor = B[step_now]
        parcial = a * factor
        msg = (
            f"👉 Multiplica el número <b>{a}</b> por el dígito "
            f"<b>{factor}</b> (columna de { _place_name(step_now) }).<br/>"
            f"Escribe el resultado parcial alineado correctamente."
        )
        board = _board(a, b, solved_lines, show_total=False)
        return {
            "status": "ask",
            "message": f"{board}{msg}",
            "expected_answer": str(parcial),
            "topic": "multiplicacion",
            "hint_type": "mul_col",
            "next_step": step_now + 1  # ✅ avance de paso
        }

    # Último paso: suma de resultados parciales
    if step_now == m:
        total = a * b
        board = _board(a, b, solved_lines, show_total=True)
        msg = (
            f"{board}✅ Muy bien. Ahora suma los productos parciales.<br/>"
            f"El resultado final es <b>{total}</b>."
        )
        return {
            "status": "done",  # ✅ cierre
            "message": msg,
            "expected_answer": str(total),
            "topic": "multiplicacion",
            "hint_type": "mul_result",
            "next_step": step_now + 1  # ✅ marca cierre limpio
        }

    # Seguridad: si se pasa de rango
    return {
        "status": "done",
        "message": "✅ Has completado correctamente la multiplicación.",
        "expected_answer": "ok",
        "topic": "multiplicacion",
        "hint_type": "mul_result",
        "next_step": step_now + 1
    }
