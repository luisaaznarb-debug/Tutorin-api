# -*- coding: utf-8 -*-
import re
from typing import List, Tuple

_PLACES = [
    "unidades", "decenas", "centenas", "millares", "decenas de millar",
    "centenas de millar", "millones", "decenas de millón", "centenas de millón"
]

def _place_name(k: int) -> str:
    return _PLACES[k] if k < len(_PLACES) else f"posición {k}"

def _norm_cycle(cycle: str | None) -> str:
    c = (cycle or "c2").strip().lower()
    if c in {"1", "c1"}: return "c1"
    if c in {"2", "c2"}: return "c2"
    if c in {"3", "c3"}: return "c3"
    return "c2"

def _parse_add(question: str) -> Tuple[int, int] | None:
    q = question.replace("＋", "+").replace("﹢", "+").replace("–", "-")
    m = re.search(r"(\d+)\s*\+\s*(\d+)", q)
    if not m:
        return None
    a, b = int(m.group(1)), int(m.group(2))
    return a, b

def _digits_rev(n: int) -> List[int]:
    return [int(ch) for ch in str(n)][::-1]

def _compute_columns(a: int, b: int):
    A = _digits_rev(a)
    B = _digits_rev(b)
    n = max(len(A), len(B))
    cols = []
    carry = 0
    for k in range(n):
        d1 = A[k] if k < len(A) else 0
        d2 = B[k] if k < len(B) else 0
        total = d1 + d2 + carry
        digit = total % 10
        new_carry = total // 10
        cols.append((d1, d2, carry, total, digit, new_carry, _place_name(k)))
        carry = new_carry
    return cols, carry

def _width(a: int, b: int) -> int:
    total = a + b
    return max(len(str(a)), len(str(b)) + 2, len(str(total))) + 2

def _board(a: int, b: int, solved_right_digits: List[int], show_sum_line: bool) -> str:
    w = _width(a, b)
    rj = lambda s: s.rjust(w)
    lines = [rj(str(a)), rj("+ " + str(b)), rj("-" * max(len(str(a)), len(str(b)) + 2))]
    partial = " ".join(str(d) for d in solved_right_digits[::-1])
    lines.append(rj(partial))
    if show_sum_line:
        lines.append(rj("-" * max(len(partial), 1)))
    return (
        "<pre style='font-family:monospace;line-height:1.25;margin:6px 0 0 0'>"
        + "\n".join(lines)
        + "</pre>"
    )

def _msg_col(a: int, b: int, col, idx: int, cycle: str) -> str:
    d1, d2, carry_in, total, digit, carry_out, place = col
    if cycle == "c1":
        extra = f" (+{carry_in})" if carry_in else ""
        return (
            f"👉 Suma la columna de <b>{place}</b>: <b>{d1}</b> + <b>{d2}</b>{extra}. "
            "Escribe solo la <b>cifra</b> que va abajo."
        )
    if cycle == "c3":
        est = d1 + d2 + (1 if carry_in else 0)
        return (
            f"👉 {place.capitalize()}: {d1}+{d2}"
            + (f"+{carry_in}" if carry_in else "")
            + f". Estima ≈ {est} y escribe la cifra (si ≥10, lleva 1)."
        )
    return (
        f"👉 {place.capitalize()}: {d1}+{d2}"
        + (f"+{carry_in}" if carry_in else "")
        + ". Si es ≥10, lleva 1."
    )

def _msg_carry(final_carry: int) -> str:
    return f"👉 Escribe la <b>llevada final</b>: <b>{final_carry}</b>."

# ──────────────────────────────────────────────
# Motor principal
# ──────────────────────────────────────────────
def handle_step(question: str, step_now: int, last_answer: str, error_count: int, cycle: str = "c2"):
    parsed = _parse_add(question)
    if not parsed:
        return None
    a, b = parsed
    cycle = _norm_cycle(cycle)
    cols, final_carry = _compute_columns(a, b)
    n = len(cols)
    num_solved = min(step_now, n)
    solved_digits = [cols[j][4] for j in range(num_solved)]

    # Paso de columnas (0 hasta n-1)
    if 0 <= step_now < n:
        board = _board(a, b, solved_right_digits=solved_digits, show_sum_line=False)
        col = cols[step_now]
        msg = _msg_col(a, b, col, step_now, cycle)
        expected = str(col[4])
        return {
            "status": "ask",
            "message": f"{board}{msg}",
            "expected_answer": expected,
            "topic": "suma",
            "hint_type": "add_col",
            "next_step": step_now + 1
        }

    # Paso de llevada final (step_now == n)
    if step_now == n and final_carry > 0:
        board = _board(a, b, solved_right_digits=solved_digits, show_sum_line=False)
        return {
            "status": "ask",
            "message": f"{board}{_msg_carry(final_carry)}",
            "expected_answer": str(final_carry),
            "topic": "suma",
            "hint_type": "add_carry",
            "next_step": step_now + 1
        }

    # Cierre final
    result_digits = [col[4] for col in cols]
    if final_carry > 0:
        result_digits.append(final_carry)
    board = _board(a, b, solved_right_digits=result_digits, show_sum_line=True)
    return {
        "status": "done",
        "message": f"{board}✅ ¡Buen trabajo! Has terminado la suma.",
        "expected_answer": str(a + b),
        "topic": "suma",
        "hint_type": "add_resultado",
        "next_step": step_now + 1
    }
