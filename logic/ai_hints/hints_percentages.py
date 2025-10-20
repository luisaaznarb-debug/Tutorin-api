# -*- coding: utf-8 -*-
"""
Pistas específicas para el motor de porcentajes.
Estas pistas acompañan a percentages_engine.py paso a paso.
"""

from logic.ai_hints.hints_utils import format_hint_message


def get_hint(hint_type: str, errors: int = 0) -> str:
    """
    Devuelve una pista educativa según el tipo de paso y número de errores.
    hint_type → valores esperados del motor:
      - perc_frac
      - perc_mult
      - perc_simplify
      - perc_result
    """
    hints = {
        # Paso 0: Interpretar porcentaje como fracción
        "perc_frac": [
            "Recuerda que <b>porcentaje</b> significa 'de cada 100'.",
            "Convierte el número en una fracción con denominador 100. Por ejemplo: 25% = 25/100.",
            "Intenta escribirlo así: <b>porcentaje / 100</b>. ¡Tú puedes!",
        ],

        # Paso 1: Multiplicación por la cantidad base
        "perc_mult": [
            "Multiplica la fracción por la cantidad base. Por ejemplo: (25/100) × 80.",
            "El número después de 'de' es el que debes multiplicar. 😉",
            "Si dudas, piensa: 25% de 80 = 80 × (25/100).",
        ],

        # Paso 2: Simplificar el resultado
        "perc_simplify": [
            "Divide entre 100 o mueve la coma dos lugares a la izquierda.",
            "Por ejemplo, 2500/100 = 25 o 80/100 = 0.8.",
            "Mira el número y quita los dos ceros del 100: es como dividir entre 100.",
        ],

        # Paso 3: Resultado final
        "perc_result": [
            "Vuelve a leer: el resultado indica cuántas partes de la cantidad base representa el porcentaje.",
            "Por ejemplo, el 25% de 80 es 20, porque 20 es una cuarta parte de 80.",
            "¡Muy bien! Así se interpreta un porcentaje en la vida real.",
        ],
    }

    # Seleccionar las pistas
    if hint_type not in hints:
        return format_hint_message(
            "No tengo una pista específica para este paso. Intenta volver a leer la pregunta con calma. 🌈"
        )

    selected = hints[hint_type]
    index = min(errors, len(selected) - 1)
    return format_hint_message(selected[index])
