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
    # Normalizar posibles signos unicode y espacios raros
    return (
        text.replace("−", "-")   # minus unicode
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
        cols.append((d1, d2, digit, _place_name(k)))
    return cols

def _board(a: int, b: int, solved_digits: List[int]) -> str:
    return (
        "<pre style='font-family:monospace;line-height:1.25;margin:6px 0 0 0'>"
        f"{a}\n- {b}\n{'-' * max(len(str(a)), len(str(b))+2)}\n"
        f"{''.join(str(d) for d in solved_digits[::-1])}</pre>"
    )

def handle_step(question: str, step_now: int, last_answer: str, error_count: int, cycle: str = "c2"):
    parsed = _detect(question)
    if not parsed:
        return None

    a, b = parsed
    # Siempre operamos con minuendo ≥ sustraendo para el formato escrito
    if a < b:
        a, b = b, a

    cols = _compute_columns(a, b)
    n = len(cols)

    # Dígitos ya resueltos a la derecha
    solved_digits = [cols[j][2] for j in range(min(step_now, n))]

    # Pasos de columnas
    if 0 <= step_now < n:
        col = cols[step_now]
        msg = (
            f"👉 Resta la columna de <b>{col[3]}</b>: <b>{col[0]}</b> − <b>{col[1]}</b>. "
            "Escribe solo la cifra que va abajo."
        )
        return {
            "status": "ask",
            "message": f"{_board(a, b, solved_digits)}{msg}",
            "expected_answer": str(col[2]),
            "topic": "resta",
            "hint_type": "sub_col",
            "next_step": step_now + 1  # ✅ añadido avance
        }

    # Cierre
    if step_now >= n:
        full = [c[2] for c in cols]
        msg = f"✅ ¡Buen trabajo! Has terminado la resta: {a} - {b} = {a - b}."
        return {
            "status": "done",
            "message": f"{_board(a, b, full)}{msg}",
            "expected_answer": "ok",
            "topic": "resta",
            "hint_type": "sub_col",
            "next_step": step_now + 1  # ✅ añadido cierre limpio
        }
