# -*- coding: utf-8 -*-
import re
from logic.ai_hints.ai_router import generate_hint_with_ai

# ──────────────────────────────────────────────
# Detección del tipo de ejercicio
# ──────────────────────────────────────────────

def _parse_statistics(question: str):
    q = question.lower().replace(",", ".")
    # Buscar números
    nums = [float(x) for x in re.findall(r"\d+(?:\.\d+)?", q)]
    if not nums:
        return None

    # Detección del tipo de ejercicio
    if "probabilidad" in q or "azar" in q or "moneda" in q or "dado" in q:
        tipo = "probabilidad"
    elif "porcentaje" in q or "%" in q or "gráfico" in q or "grafico" in q:
        tipo = "porcentaje"
    elif "frecuencia" in q or "encuesta" in q:
        tipo = "frecuencia"
    else:
        tipo = "probabilidad"  # por defecto

    return tipo, nums


# ──────────────────────────────────────────────
# Motor principal
# ──────────────────────────────────────────────

def handle_step(question: str, step_now: int, last_answer: str, error_count: int, cycle: str = "c2"):
    parsed = _parse_statistics(question)
    if not parsed:
        return None
    tipo, nums = parsed

    # Interpretación base: 2 números → casos favorables / totales
    if len(nums) >= 2:
        favorables, total = nums[0], nums[1]
    else:
        favorables, total = nums[0], 1.0

    # Paso 0 → identificar los datos
    if step_now == 0:
        msg = (
            f"👉 Tenemos <b>{favorables}</b> casos favorables de un total de <b>{total}</b>.<br/>"
            f"Vamos a calcular la {'probabilidad' if tipo=='probabilidad' else 'frecuencia'} correspondiente.<br/>"
            "¿Qué operación debemos realizar?"
        )
        return {
            "status": "ask",
            "message": msg,
            "expected_answer": "favorables/total",
            "topic": "estadistica",
            "hint_type": "stat_intro",
            "next_step": step_now + 1
        }

    # Paso 1 → plantear la fracción o proporción
    if step_now == 1:
        msg = (
            f"✅ Correcto.<br/>Planteamos la fracción: "
            f"<b>{favorables}/{total}</b>.<br/>"
            "¿Puedes simplificarla o calcular su valor decimal?"
        )
        result = favorables / total
        return {
            "status": "ask",
            "message": msg,
            "expected_answer": f"{favorables}/{total}",
            "topic": "estadistica",
            "hint_type": "stat_frac",
            "next_step": step_now + 1
        }

    # Paso 2 → conversión a número decimal
    if step_now == 2:
        prob = round(favorables / total, 3)
        msg = (
            f"👉 Divide los casos favorables entre el total:<br/>"
            f"{favorables} ÷ {total} = <b>{prob}</b>."
        )
        return {
            "status": "ask",
            "message": msg,
            "expected_answer": str(prob),
            "topic": "estadistica",
            "hint_type": "stat_decimal",
            "next_step": step_now + 1
        }

    # Paso 3 → conversión a porcentaje (si aplica)
    if step_now == 3:
        prob = round(favorables / total, 3)
        perc = round(prob * 100, 1)
        msg = (
            f"👉 Si multiplicamos por 100 obtenemos el porcentaje:<br/>"
            f"{prob} × 100 = <b>{perc}%</b>."
        )
        return {
            "status": "ask",
            "message": msg,
            "expected_answer": f"{perc}%",
            "topic": "estadistica",
            "hint_type": "stat_percent",
            "next_step": step_now + 1
        }

    # Paso 4 → interpretación final
    if step_now == 4:
        prob = round(favorables / total, 3)
        perc = round(prob * 100, 1)
        msg = (
            f"✅ ¡Muy bien! 🎉<br/>"
            f"La {'probabilidad' if tipo=='probabilidad' else 'frecuencia relativa'} es "
            f"<b>{prob}</b> (equivale a <b>{perc}%</b>).<br/>"
            f"Esto significa que ocurrirá aproximadamente <b>{perc}%</b> de las veces."
        )
        return {
            "status": "done",
            "message": msg,
            "expected_answer": f"{prob}",
            "topic": "estadistica",
            "hint_type": "stat_result",
            "next_step": step_now + 1
        }

    # Seguridad
    return {
        "status": "done",
        "message": "✅ Has completado correctamente el ejercicio de probabilidad o gráficos.",
        "expected_answer": "ok",
        "topic": "estadistica",
        "hint_type": "stat_result",
        "next_step": step_now + 1
    }
