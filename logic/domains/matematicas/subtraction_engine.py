# -*- coding: utf-8 -*-
from typing import List, Tuple, Optional
import re

_PLACES = [
    "unidades", "decenas", "centenas", "millares", "decenas de millar",
    "centenas de millar", "millones"
]

def _place_name(k: int) -> str:
    return _PLACES[k] if k < len(_PLACES) else f"posición {k}"

def _normalize(text: str) -> str:
    return (
        text.replace("−", "-")
        .replace("—", "-")
        .replace("–", "-")
        .replace("÷", "/")
        .replace("×", "*")
        .replace("·", "*")
    )

def _detect(question: str) -> Optional[Tuple[int, int]]:
    q = _normalize(question)
    m = re.search(r"(\d+)\s*-\s*(\d+)", q)
    return (int(m.group(1)), int(m.group(2))) if m else None

def _digits_rev(n: int) -> List[int]:
    return [int(ch) for ch in str(n)][::-1]

def _compute_columns(a: int, b: int):
    A = _digits_rev(a)
    B = _digits_rev(b)
    n = max(len(A), len(B))
    cols = []
    borrow = 0
    for k in range(n):
        d1 = A[k] if k < len(A) else 0
        d2 = B[k] if k < len(B) else 0
        raw = d1 - borrow - d2
        if raw < 0:
            digit = raw + 10
            borrow = 1
        else:
            digit = raw
            borrow = 0
        needs_borrow = (d1 - borrow < d2) if k == 0 else (d1 - borrow < d2)
        cols.append((d1, d2, digit, _place_name(k), needs_borrow))
    return cols, borrow

def _board(a: int, b: int, solved_digits: List[int]) -> str:
    return (
        "<pre style='font-family:monospace;line-height:1.25;margin:6px 0 0 0'>"
        f"{a}\n- {b}\n{'-' * max(len(str(a)), len(str(b)) + 2)}\n"
        f"{' '.join(str(d) for d in solved_digits[::-1])}</pre>"
    )

def handle_step(question: str, step_now: int, last_answer: str, error_count: int, cycle: str = "c2"):
    parsed = _detect(question)
    if not parsed:
        return None
    a, b = parsed
    if a < b:
        a, b = b, a
    cols, final_borrow = _compute_columns(a, b)
    n = len(cols)
    solved_digits = [cols[j][2] for j in range(min(step_now, n))]

    if 0 <= step_now < n:
        d1, d2, digit, place, needs_borrow = cols[step_now]
        hint_type = "sub_borrow" if needs_borrow else "sub_col"
        msg = (
            f"👉 Resta la columna de <b>{place}</b>: <b>{d1}</b> − <b>{d2}</b>. "
            "Escribe solo la cifra que va abajo."
        )
        return {
            "status": "ask",
            "message": f"{_board(a, b, solved_digits)}{msg}",
            "expected_answer": str(digit),
            "topic": "resta",
            "hint_type": hint_type,
            "next_step": step_now + 1
        }

    if step_now >= n:
        full = [c[2] for c in cols]
        msg = f"✅ ¡Buen trabajo! Has terminado la resta: {a} - {b} = {a - b}."
        return {
            "status": "done",
            "message": f"{_board(a, b, full)}{msg}",
            "expected_answer": "ok",
            "topic": "resta",
            "hint_type": "sub_resultado",
            "next_step": step_now + 1
        }
