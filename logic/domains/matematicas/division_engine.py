# -*- coding: utf-8 -*-
import re
from typing import List, Dict, Tuple
from logic.ai_hints.ai_router import generate_hint_with_ai


# ──────────────────────────────────────────────
# Funciones auxiliares
# ──────────────────────────────────────────────

def _parse_div(q: str):
    q2 = q.replace("÷", "/").replace(":", "/")
    m = re.search(r"(\d+)\s*/\s*(\d+)", q2)
    if not m:
        return None
    a, b = int(m.group(1)), int(m.group(2))
    if b == 0:
        return None
    return a, b


def _first_group_len(dividend: int, divisor: int) -> int:
    s = str(dividend)
    k = 1
    while k < len(s) and int(s[:k]) < divisor:
        k += 1
    return k


def _compute_steps(dividend: int, divisor: int) -> Tuple[List[Dict], int, int, int]:
    s = str(dividend)
    n = len(s)
    first_k = _first_group_len(dividend, divisor)
    group = int(s[:first_k])

    steps: List[Dict] = []
    quotient_str = ""
    pos = first_k

    while True:
        qdigit = group // divisor
        product = qdigit * divisor
        remainder = group - product
        quotient_str += str(qdigit)

        item = {"group": group, "qdigit": qdigit, "product": product,
                "remainder": remainder, "quotient_prefix": quotient_str}

        if pos < n:
            next_digit = int(s[pos])
            new_group = remainder * 10 + next_digit
            item["next_digit"] = next_digit
            item["new_group"] = new_group
            steps.append(item)
            group = new_group
            pos += 1
        else:
            steps.append(item)
            break

    quotient_full = int(quotient_str)
    remainder_final = steps[-1]["remainder"]
    return steps, quotient_full, remainder_final, first_k


def _render_pre_left_dividend(dividend: int, divisor: int, steps: List[Dict],
                              first_k: int, block: int, sub: int,
                              show_full_quotient: bool = False) -> str:
    s_div = str(dividend)
    s_divisor = str(divisor)
    L = len(s_div)
    SEP_BAR = " | "
    SEP = "   "

    confirmed = block + (1 if sub >= 1 else 0)
    q_parcial = steps[block]["quotient_prefix"][:confirmed] if block < len(steps) else steps[-1]["quotient_prefix"]
    q_shown = (steps[-1]["quotient_prefix"] if show_full_quotient else q_parcial) or ""

    rows: List[str] = []
    rows.append(f"{s_div}{SEP_BAR}{s_divisor}")
    rows.append(" " * L + SEP + q_shown)

    return (
        "<pre style='font-family:monospace;line-height:1.25;margin:6px 0 0 0'>"
        + "\n".join(rows)
        + "</pre>"
    )


def _intro_group(dividend: int, divisor: int, cycle: str) -> str:
    return (f"👉 Elige el <b>primer grupo del dividendo</b> que sea <b>≥</b> al <b>divisor</b>. "
            f"Dividendo: <b>{dividend}</b>, divisor: <b>{divisor}</b>.")


# ──────────────────────────────────────────────
# Motor principal (corregido con control de pasos)
# ──────────────────────────────────────────────

def handle_step(question: str, step_now: int, last_answer: str, error_count: int, cycle: str = "c2"):
    parsed = _parse_div(question)
    if not parsed:
        return None

    dividend, divisor = parsed
    steps, q_full, r_final, first_k = _compute_steps(dividend, divisor)
    subcounts = [3] * (len(steps) - 1) + [2]  # pasos internos por bloque

    # Paso inicial: identificar primer grupo
    if step_now == 0:
        pre = _render_pre_left_dividend(dividend, divisor, steps, first_k, block=0, sub=0)
        msg = (f"{pre}{_intro_group(dividend, divisor, cycle)} "
               "¿Con qué número empezamos? Escribe solo ese número.")
        return {
            "status": "ask",
            "message": msg,
            "expected_answer": str(int(str(dividend)[:first_k])),
            "topic": "division",
            "hint_type": "div_grupo",
            "next_step": step_now + 1  # ✅ avance inicial
        }

    # Cálculo del bloque actual
    s = step_now - 1
    block = 0
    while block < len(subcounts) and s >= subcounts[block]:
        s -= subcounts[block]
        block += 1

    # Si ya hemos completado todos los bloques
    if block >= len(steps):
        pre = _render_pre_left_dividend(
            dividend, divisor, steps, first_k, block=len(steps) - 1, sub=2, show_full_quotient=True
        )
        msg = f"{pre}✅ ¡Buen trabajo! Has completado la división."
        return {
            "status": "done",
            "message": msg,
            "expected_answer": "ok",
            "topic": "division",
            "hint_type": "div_result",
            "next_step": step_now + 1  # ✅ cierre
        }

    # Paso dentro del bloque actual
    step_data = steps[block]
    msg = ""
    expected = ""

    if s == 0:
        msg = f"👉 ¿Cuántas veces cabe <b>{divisor}</b> en <b>{step_data['group']}</b> sin pasarte?"
        expected = str(step_data["qdigit"])
    elif s == 1:
        msg = f"Resta {step_data['group']} − {divisor}×{step_data['qdigit']}."
        expected = str(step_data["remainder"])
    elif s == 2 and "next_digit" in step_data:
        msg = f"Baja la siguiente cifra: {step_data['next_digit']}. ¿Qué número queda?"
        expected = str(step_data["new_group"])
    else:
        msg = "Sigamos con la división."
        expected = "ok"

    pre = _render_pre_left_dividend(dividend, divisor, steps, first_k, block, s)
    return {
        "status": "ask",
        "message": f"{pre}{msg}",
        "expected_answer": expected,
        "topic": "division",
        "hint_type": "div_step",
        "next_step": step_now + 1  # ✅ avance por paso
    }
