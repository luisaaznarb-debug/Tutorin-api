# -*- coding: utf-8 -*-
import re
from logic.domains.matematicas import (
    addition_engine,
    subtraction_engine,
    multiplication_engine,
    division_engine,
    fractions_engine,
    percentages_engine,
    measures_engine,
    geometry_engine,
    statistics_engine,
)

# ──────────────────────────────────────────────
# Identificador del tipo de problema
# ──────────────────────────────────────────────

def _detect_engine(question: str):
    q = question.lower()

    if any(x in q for x in ["más", "+", "suma", "añadir", "total", "en conjunto"]):
        return addition_engine
    if any(x in q for x in ["menos", "-", "resta", "quedan", "diferencia"]):
        return subtraction_engine
    if any(x in q for x in ["multiplica", "producto", "veces", "×", "por cada"]):
        return multiplication_engine
    if any(x in q for x in ["divide", "reparte", "entre", "÷"]):
        return division_engine
    if any(x in q for x in ["fracción", "fraccion", "/", "partes iguales"]):
        return fractions_engine
    if any(x in q for x in ["porcentaje", "%", "por ciento"]):
        return percentages_engine
    if any(x in q for x in ["km", "cm", "kg", "g", "ml", "l", "litros", "metros", "unidad de medida"]):
        return measures_engine
    if any(x in q for x in ["área", "perímetro", "figura", "triángulo", "cuadrado", "círculo"]):
        return geometry_engine
    if any(x in q for x in ["gráfico", "probabilidad", "frecuencia", "encuesta", "dado", "moneda"]):
        return statistics_engine

    return None


# ──────────────────────────────────────────────
# Motor principal combinador
# ──────────────────────────────────────────────

def handle_step(question: str, step_now: int, last_answer: str, error_count: int, cycle: str = "c2"):
    engine = _detect_engine(question)

    if not engine:
        return {
            "status": "done",
            "message": (
                "❓ No he podido identificar el tipo de problema.<br/>"
                "Intenta reformularlo con palabras como <b>suma</b>, <b>resta</b>, "
                "<b>porcentaje</b> o <b>área</b>."
            ),
            "expected_answer": "error",
            "topic": "problemas",
            "hint_type": "problem_unknown",
            "next_step": step_now + 1
        }

    # Llamada dinámica al motor correspondiente
    try:
        result = engine.handle_step(question, step_now, last_answer, error_count, cycle)
        if result:
            # Añadimos la referencia del motor para seguimiento (sin cambiar topic)
            result["source_engine"] = engine.__name__.replace("_engine", "")
            # NO sobrescribimos result["topic"] → se mantiene el original (suma, resta, etc.)
            return result
        else:
            raise Exception("Motor sin respuesta válida.")
    except Exception as e:
        return {
            "status": "done",
            "message": f"⚠️ Error al procesar con el motor {engine.__name__}: {str(e)}",
            "expected_answer": "error",
            "topic": "problemas",  # solo en errores
            "hint_type": "problem_error",
            "next_step": step_now + 1
        }
