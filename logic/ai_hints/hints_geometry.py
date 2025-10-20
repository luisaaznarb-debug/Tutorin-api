# -*- coding: utf-8 -*-
"""
Pistas educativas para el motor de geometría (geometry_engine.py)
Tutorín acompaña al alumno a recordar fórmulas, sustituir valores y razonar el resultado.
"""

from logic.ai_hints.hints_utils import format_hint_message


def get_hint(hint_type: str, errors: int = 0) -> str:
    """
    Devuelve una pista según el tipo de paso y el número de errores.
    hint_type → valores esperados del motor:
      - geo_formula
      - geo_substitute
      - geo_calc
      - geo_result
    """
    hints = {
        # Paso 0: recordar la fórmula
        "geo_formula": [
            "Piensa qué figura geométrica estás trabajando. Cada una tiene su fórmula propia.",
            "Por ejemplo: cuadrado → lado × lado, triángulo → base × altura ÷ 2.",
            "Si dudas, imagina dibujar la figura y recuerda cuántos lados o dimensiones tiene.",
        ],

        # Paso 1: sustituir valores
        "geo_substitute": [
            "Sustituye los valores que aparecen en el problema dentro de la fórmula.",
            "Por ejemplo: si base = 8 y altura = 5, entonces área = 8 × 5 ÷ 2.",
            "Ten cuidado con el orden: primero base, luego altura o radio según la figura.",
        ],

        # Paso 2: realizar el cálculo numérico
        "geo_calc": [
            "Multiplica o divide los números según la fórmula. Hazlo paso a paso.",
            "Recuerda usar el orden correcto de operaciones: multiplicaciones antes que sumas.",
            "Redondea el resultado si tiene muchos decimales. 😊",
        ],

        # Paso 3: interpretar el resultado final
        "geo_result": [
            "Piensa qué representa el número: si es área, son unidades cuadradas (cm², m²...).",
            "Si es perímetro, representa la longitud del borde (cm, m...).",
            "Revisa si el número tiene sentido con el tamaño de la figura. ¡Buen trabajo!",
        ],
    }

    if hint_type not in hints:
        return format_hint_message(
            "No tengo una pista específica para este paso, pero recuerda: identifica la figura, usa la fórmula y calcula con calma. 📐"
        )

    selected = hints[hint_type]
    index = min(errors, len(selected) - 1)
    return format_hint_message(selected[index])
