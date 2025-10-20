# -*- coding: utf-8 -*-
"""
Pistas educativas para el motor de resolución de problemas combinados
(problem_solving_engine.py)
Tutorín enseña a razonar, identificar operaciones y verificar resultados.
"""

from logic.ai_hints.hints_utils import format_hint_message


def get_hint(hint_type: str, errors: int = 0) -> str:
    """
    Devuelve una pista educativa adaptada al tipo de ayuda que Tutorín puede ofrecer.
    Este motor no se basa en pasos numéricos, sino en estrategias de resolución.
    hint_type → puede ser:
      - problem_understand
      - problem_plan
      - problem_execute
      - problem_check
      - problem_error
    """
    hints = {
        # Paso 0 → comprensión del enunciado
        "problem_understand": [
            "Lee despacio el enunciado y subraya los datos más importantes. ✍️",
            "Pregúntate: ¿Qué me pide exactamente el problema?",
            "Identifica las palabras clave: 'más', 'menos', 'cada', 'mitad', 'porcentaje'...",
        ],

        # Paso 1 → planificación
        "problem_plan": [
            "Piensa qué tipo de operación necesitas: suma, resta, multiplicación, división o porcentaje.",
            "Si hay varias etapas, resuelve una a una (primero el total, luego la parte, etc.).",
            "Recuerda que puedes dibujar o hacer una tabla para organizar la información. 📊",
        ],

        # Paso 2 → ejecución del cálculo
        "problem_execute": [
            "Aplica la operación que hayas elegido con cuidado.",
            "Verifica que usas los números correctos del enunciado.",
            "Escribe el proceso paso a paso para no saltarte nada. 🧮",
        ],

        # Paso 3 → comprobación
        "problem_check": [
            "Vuelve al enunciado y comprueba si tu respuesta responde a la pregunta.",
            "Mira si el resultado tiene sentido (¿puede haber 150 niños en un aula?).",
            "Si no te convence, revisa la operación o repite el razonamiento. 🔁",
        ],

        # Paso 4 → error general
        "problem_error": [
            "Parece que hay un error en los datos o en la operación. No pasa nada, revisa el enunciado. 💪",
            "A veces un pequeño detalle cambia el tipo de operación. ¿Estás seguro de haber elegido la correcta?",
            "Prueba a escribir el problema con tus propias palabras: te ayudará a entenderlo mejor.",
        ],
    }

    if hint_type not in hints:
        return format_hint_message(
            "No tengo una pista exacta para este tipo de problema, pero recuerda: lee, piensa, planifica, resuelve y revisa. 🌈"
        )

    selected = hints[hint_type]
    index = min(errors, len(selected) - 1)
    return format_hint_message(selected[index])
