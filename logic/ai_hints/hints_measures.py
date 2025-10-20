# -*- coding: utf-8 -*-
"""
Pistas para el motor de medidas y unidades (measures_engine.py)
Tutorín ayuda paso a paso a comprender la relación entre unidades del SI.
"""

from logic.ai_hints.hints_utils import format_hint_message


def get_hint(hint_type: str, errors: int = 0) -> str:
    """
    Devuelve una pista educativa según el tipo de paso y número de errores.
    hint_type → valores esperados del motor:
      - meas_estimate
      - meas_factor
      - meas_calc
      - meas_result
    """
    hints = {
        # Paso 0: Estimar si el número aumenta o disminuye
        "meas_estimate": [
            "Piensa si la unidad nueva es <b>más pequeña o más grande</b>.",
            "Si pasas de kilómetros a metros, hay <b>más</b> unidades, así que el número será <b>mayor</b>.",
            "Si pasas de metros a kilómetros, hay <b>menos</b> unidades, así que el número será <b>menor</b>.",
        ],

        # Paso 1: Recordar el factor de conversión
        "meas_factor": [
            "Cada salto en la tabla de unidades multiplica o divide por 10, 100 o 1000.",
            "Por ejemplo: 1 km = 1000 m, 1 m = 100 cm, 1 l = 1000 ml.",
            "Busca el factor en la tabla: km → m (×1000), m → km (÷1000).",
        ],

        # Paso 2: Realizar el cálculo
        "meas_calc": [
            "Multiplica o divide según la dirección del cambio.",
            "Si cambias a una unidad más pequeña, multiplica; si es más grande, divide.",
            "Ejemplo: 3 km → m → 3 × 1000 = 3000 m.",
        ],

        # Paso 3: Interpretar el resultado final
        "meas_result": [
            "Revisa si el resultado tiene sentido: ¿es lógico que aumente o disminuya?",
            "Por ejemplo: 2500 ml son 2.5 litros (más grande la unidad → número más pequeño).",
            "¡Muy bien! Ya dominas las equivalencias entre unidades.",
        ],
    }

    if hint_type not in hints:
        return format_hint_message(
            "No tengo una pista específica para este paso, pero recuerda usar la tabla de unidades para orientarte. 📏"
        )

    selected = hints[hint_type]
    index = min(errors, len(selected) - 1)
    return format_hint_message(selected[index])
