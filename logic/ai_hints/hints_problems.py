# -*- coding: utf-8 -*-
"""
hints_problems.py
Pistas progresivas para resolución de problemas combinados según nivel de error.
Compatible con problem_solving_engine.py
"""

from typing import Optional

def get_hint(hint_type: str, errors: int = 0) -> str:
    """
    Devuelve una pista educativa adaptada al tipo de ayuda que Tutorín puede ofrecer.
    Este motor no se basa en pasos numéricos, sino en estrategias de resolución.
    
    Args:
        hint_type: tipo de estrategia ('problem_understand', 'problem_plan', etc.)
        errors: nivel de error (0-4+)
    """
    errors = max(0, min(int(errors or 0), 4))

    # ────────── COMPRENSIÓN DEL ENUNCIADO ──────────
    if hint_type == "problem_understand" or hint_type == "prob_comprension":
        if errors == 0:
            return (
                "👉 Lee despacio el enunciado y subraya los datos más importantes. "
                "Pregúntate: ¿Qué me pide exactamente el problema? ✍️"
            )
        elif errors == 1:
            return (
                "🧮 Identifica las palabras clave: 'más', 'menos', 'cada', 'mitad', 'porcentaje', 'total'... "
                "Esas palabras te indican qué operación necesitas."
            )
        elif errors == 2:
            return (
                "💡 Estrategia de lectura:\n"
                "1. Lee el problema completo\n"
                "2. Subraya los números y unidades\n"
                "3. Identifica qué te preguntan\n"
                "4. Piensa qué datos necesitas para responder"
            )
        else:
            return (
                "✅ Haz un dibujo o esquema si te ayuda a visualizar el problema. "
                "A veces ver la situación dibujada hace que todo sea más claro."
            )

    # ────────── PLANIFICACIÓN ──────────
    if hint_type == "problem_plan":
        if errors == 0:
            return (
                "👉 Piensa qué tipo de operación necesitas: "
                "suma, resta, multiplicación, división o porcentaje."
            )
        elif errors == 1:
            return (
                "🧮 Si hay varias etapas, resuelve una a una. "
                "Por ejemplo: primero calcula el total, luego la parte, etc."
            )
        elif errors == 2:
            return (
                "💡 Puedes hacer una tabla o lista:\n"
                "- ¿Qué sé? (datos del problema)\n"
                "- ¿Qué busco? (lo que me preguntan)\n"
                "- ¿Qué operación necesito? 📊"
            )
        else:
            return (
                "✅ Ejemplo de planificación:\n"
                "Problema: 'Ana tiene 24 caramelos y reparte 1/3 a su hermano. ¿Cuántos le quedan?'\n"
                "Plan: 1) Calcular 1/3 de 24 (división o multiplicación)\n"
                "      2) Restar ese resultado de 24"
            )

    # ────────── EJECUCIÓN DEL CÁLCULO ──────────
    if hint_type == "problem_execute" or hint_type == "prob_operacion" or hint_type == "prob_calculo":
        if errors == 0:
            return (
                "👉 Aplica la operación que hayas elegido con cuidado. "
                "Verifica que usas los números correctos del enunciado. 🧮"
            )
        elif errors == 1:
            return (
                "🧮 Escribe el proceso paso a paso para no saltarte nada. "
                "Ejemplo: '24 ÷ 3 = 8, luego 24 - 8 = 16'."
            )
        elif errors == 2:
            return (
                "💡 Comprueba que la operación tenga sentido:\n"
                "- Si el problema dice 'en total', probablemente sea suma\n"
                "- Si dice 'quedan' o 'faltan', probablemente sea resta\n"
                "- Si dice 'cada' o 'veces', probablemente sea multiplicación"
            )
        else:
            return (
                "✅ Usa la calculadora si lo necesitas, pero asegúrate de escribir bien los números. "
                "Revisa que no hayas intercambiado ningún dato."
            )

    # ────────── COMPROBACIÓN ──────────
    if hint_type == "problem_check" or hint_type == "prob_comprobacion":
        if errors == 0:
            return (
                "👉 Vuelve al enunciado y comprueba si tu respuesta responde a la pregunta. "
                "Mira si el resultado tiene sentido (¿puede haber 150 niños en un aula?). 🔁"
            )
        elif errors == 1:
            return (
                "🧮 Haz una estimación rápida: ¿el resultado es muy grande o muy pequeño? "
                "Si no te convence, revisa la operación."
            )
        elif errors == 2:
            return (
                "💡 Estrategia de comprobación:\n"
                "1. Lee la pregunta de nuevo\n"
                "2. Comprueba que tu respuesta tenga las unidades correctas (euros, metros, etc.)\n"
                "3. Verifica que el número sea lógico en el contexto"
            )
        else:
            return (
                "✅ Prueba a hacer la operación inversa:\n"
                "- Si hiciste una suma, resta para comprobar\n"
                "- Si hiciste una multiplicación, divide para verificar"
            )

    # ────────── ERROR GENERAL ──────────
    if hint_type == "problem_error":
        if errors == 0:
            return (
                "😅 Parece que hay un error en los datos o en la operación. "
                "No pasa nada, revisa el enunciado con calma. 💪"
            )
        elif errors == 1:
            return (
                "🧮 A veces un pequeño detalle cambia el tipo de operación. "
                "¿Estás seguro de haber elegido la correcta?"
            )
        elif errors == 2:
            return (
                "💡 Prueba a escribir el problema con tus propias palabras: "
                "te ayudará a entenderlo mejor."
            )
        else:
            return (
                "✅ Vuelve al principio: lee, identifica datos, elige operación, calcula y comprueba. "
                "Paso a paso llegarás a la solución."
            )

    # ────────── FALLBACK ──────────
    return (
        "🤔 No tengo una pista exacta para este tipo de problema, pero recuerda: "
        "lee, piensa, planifica, resuelve y revisa. 🌈"
    )

# ────────── Integración con OpenAI ──────────
try:
    from openai import OpenAI
    import os
    _client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    _USE_AI = bool(os.getenv("OPENAI_API_KEY"))
except Exception:
    _client = None
    _USE_AI = False

PROMPT = (
    "Eres Tutorín (profesor de Primaria, LOMLOE). Da pistas concisas (1–2 frases) "
    "para resolución de problemas. Enseña estrategias, no des la solución. "
    "Paso: {step} | Errores: {err}"
)

def _ai_hint(hint_type: str, err: int) -> Optional[str]:
    """Genera pista con OpenAI si err >= 2."""
    if not _USE_AI or not _client or err < 2:
        return None
    
    try:
        res = _client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": "Eres un profesor de Primaria empático y paciente."},
                {"role": "user", "content": PROMPT.format(step=hint_type, err=err)},
            ],
            temperature=0.4,
            max_tokens=120,
        )
        return (res.choices[0].message.content or "").strip()
    except Exception:
        return None