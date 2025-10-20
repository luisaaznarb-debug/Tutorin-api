# -*- coding: utf-8 -*-
"""
Pistas educativas para el motor de estadística y probabilidad (statistics_engine.py)
Tutorín ayuda a interpretar datos, frecuencias y probabilidades paso a paso.
"""

from logic.ai_hints.hints_utils import format_hint_message


def get_hint(hint_type: str, errors: int = 0) -> str:
    """
    Devuelve una pista según el tipo de paso y número de errores.
    hint_type → valores esperados del motor:
      - stat_intro
      - stat_frac
      - stat_decimal
      - stat_percent
      - stat_result
    """
    hints = {
        # Paso 0: identificar datos (casos favorables y totales)
        "stat_intro": [
            "Busca cuántos casos son favorables y cuál es el total de casos observados.",
            "Por ejemplo: si 5 de 20 alumnos prefieren azul, favorables=5 y total=20.",
            "La probabilidad o frecuencia se calcula comparando esas dos cantidades.",
        ],

        # Paso 1: plantear la fracción o proporción
        "stat_frac": [
            "Escribe la fracción con los datos: favorables / total.",
            "Por ejemplo: 5/20 representa 5 de cada 20.",
            "Si puedes, simplifica la fracción dividiendo ambos números por el mismo valor.",
        ],

        # Paso 2: convertir a decimal
        "stat_decimal": [
            "Divide los casos favorables entre el total para obtener el número decimal.",
            "Por ejemplo: 5 ÷ 20 = 0.25.",
            "Este número decimal muestra la probabilidad o frecuencia en forma numérica.",
        ],

        # Paso 3: convertir a porcentaje
        "stat_percent": [
            "Multiplica el número decimal por 100 para transformarlo en porcentaje.",
            "Por ejemplo: 0.25 × 100 = 25%.",
            "El porcentaje indica cuántas veces ocurrirá de cada 100 intentos o personas.",
        ],

        # Paso 4: interpretar el resultado
        "stat_result": [
            "Piensa qué significa el resultado: 0.25 o 25% es una de cada cuatro veces.",
            "Compara con la realidad: ¿tiene sentido que sea tan probable o tan poco probable?",
            "¡Muy bien! Así interpretas probabilidades y porcentajes en gráficos o encuestas.",
        ],
    }

    if hint_type not in hints:
        return format_hint_message(
            "No tengo una pista específica para este paso, pero recuerda: compara los casos favorables con el total y piensa qué representa el resultado. 📊"
        )

    selected = hints[hint_type]
    index = min(errors, len(selected) - 1)
    return format_hint_message(selected[index])
