# -*- coding: utf-8 -*-
import re
from logic.ai_hints.ai_router import generate_hint_with_ai

# ──────────────────────────────────────────────────────────────
# Motor de porcentajes
# ──────────────────────────────────────────────────────────────

def _parse_percentage(question: str):
    """Detecta expresiones tipo '25% de 80' o '30 por ciento de 50'."""
    q = question.lower().replace("por ciento", "%").replace("percent", "%")
    m = re.search(r"(\d+)\s*%\s*(de|of)?\s*(\d+)", q)
    if m:
        percent = int(m.group(1))
        base = int(m.group(3))
        return percent, base
    return None


def handle_step(question: str, step_now: int, last_answer: str, error_count: int, cycle: str = "c2"):
    parsed = _parse_percentage(question)
    if not parsed:
        return None
    percent, base = parsed

    # Paso 0 → reconocer la estructura
    if step_now == 0:
        msg = (
            f"👉 Vamos a calcular el <b>{percent}% de {base}</b>.<br/>"
            "Primero recuerda que <b>porcentaje</b> significa 'de cada 100'.<br/>"
            "¿Cuál es la fracción equivalente a este porcentaje?"
        )
        expected = f"{percent}/100"
        return {
            "status": "ask",
            "message": msg,
            "expected_answer": expected,
            "topic": "porcentajes",
            "hint_type": "perc_frac",
            "next_step": step_now + 1
        }

    # Paso 1 → plantear la multiplicación
    if step_now == 1:
        msg = (
            f"✅ Muy bien.<br/>Ahora calcula el <b>{percent}%</b> como una fracción de {base}:<br/>"
            f"{percent}/100 × {base}."
        )
        expected = str(percent * base) + "/100"
        return {
            "status": "ask",
            "message": msg,
            "expected_answer": expected,
            "topic": "porcentajes",
            "hint_type": "perc_mult",
            "next_step": step_now + 1
        }

    # Paso 2 → simplificar el resultado
    if step_now == 2:
        raw = percent * base
        msg = (
            f"👉 Ahora simplifica el resultado:<br/>"
            f"{raw}/100 = ?<br/>Divide entre 100 o mueve la coma dos lugares a la izquierda."
        )
        expected = str(round(raw / 100, 2))
        return {
            "status": "ask",
            "message": msg,
            "expected_answer": expected,
            "topic": "porcentajes",
            "hint_type": "perc_simplify",
            "next_step": step_now + 1
        }

    # Paso 3 → resultado final
    if step_now == 3:
        result = round(percent * base / 100, 2)
        msg = (
            f"✅ ¡Muy bien hecho! 🎉<br/>"
            f"El <b>{percent}% de {base}</b> es <b>{result}</b>.<br/>"
            f"Has aplicado correctamente la equivalencia: {percent}% = {percent}/100."
        )
        return {
            "status": "done",
            "message": msg,
            "expected_answer": str(result),
            "topic": "porcentajes",
            "hint_type": "perc_result",
            "next_step": step_now + 1
        }

    # Seguridad
    return {
        "status": "done",
        "message": "✅ Has completado correctamente el ejercicio de porcentajes.",
        "expected_answer": "ok",
        "topic": "porcentajes",
        "hint_type": "perc_result",
        "next_step": step_now + 1
    }
