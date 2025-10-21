# -*- coding: utf-8 -*-
"""
hints_statistics.py
Pistas progresivas para estadística y probabilidad según nivel de error.
Compatible con statistics_engine.py
"""

from typing import Optional

def get_hint(hint_type: str, errors: int = 0) -> str:
    """
    Devuelve una pista según el tipo de paso y número de errores.
    
    Args:
        hint_type: tipo de paso del motor de estadística
        errors: nivel de error (0-4+)
    """
    errors = max(0, min(int(errors or 0), 4))

    # ────────── IDENTIFICAR DATOS (CASOS FAVORABLES Y TOTALES) ──────────
    if hint_type == "stat_intro" or hint_type == "data_leer":
        if errors == 0:
            return (
                "👉 Busca cuántos <b>casos favorables</b> hay y cuál es el <b>total de casos</b> observados. "
                "Por ejemplo: si 5 de 20 alumnos prefieren azul, favorables=5 y total=20."
            )
        elif errors == 1:
            return (
                "🧮 Los casos favorables son los que cumplen la condición que buscas. "
                "El total es la suma de todos los casos posibles."
            )
        elif errors == 2:
            return (
                "💡 Ejemplo: si lanzas un dado y quieres saber la probabilidad de sacar par:\n"
                "- Casos favorables: 2, 4, 6 → 3 casos\n"
                "- Total de casos: 1, 2, 3, 4, 5, 6 → 6 casos"
            )
        else:
            return (
                "✅ La probabilidad o frecuencia se calcula comparando esas dos cantidades: "
                "favorables / total."
            )

    # ────────── PLANTEAR LA FRACCIÓN O PROPORCIÓN ──────────
    if hint_type == "stat_frac" or hint_type == "data_interpretar":
        if errors == 0:
            return (
                "👉 Escribe la fracción con los datos: <b>favorables / total</b>. "
                "Por ejemplo: 5/20 representa 5 de cada 20."
            )
        elif errors == 1:
            return (
                "🧮 Si puedes, simplifica la fracción dividiendo ambos números por el mismo valor. "
                "Ejemplo: 5/20 = 1/4 (dividiendo entre 5)."
            )
        elif errors == 2:
            return (
                "💡 La fracción te indica la proporción:\n"
                "- 1/2 significa 1 de cada 2 (50%)\n"
                "- 1/4 significa 1 de cada 4 (25%)\n"
                "- 3/10 significa 3 de cada 10 (30%)"
            )
        else:
            return (
                "✅ Ejemplo completo:\n"
                "Si 8 de 40 alumnos tienen gafas:\n"
                "Fracción: 8/40 = 1/5 (simplificado)\n"
                "Significa 1 de cada 5 alumnos."
            )

    # ────────── CONVERTIR A DECIMAL ──────────
    if hint_type == "stat_decimal" or hint_type == "data_comparar":
        if errors == 0:
            return (
                "👉 Divide los casos favorables entre el total para obtener el número decimal. "
                "Por ejemplo: 5 ÷ 20 = 0,25."
            )
        elif errors == 1:
            return (
                "🧮 Este número decimal muestra la probabilidad o frecuencia en forma numérica. "
                "Valores cercanos a 0 son muy poco probables, cercanos a 1 son muy probables."
            )
        elif errors == 2:
            return (
                "💡 Escala de probabilidad:\n"
                "- 0,00 = imposible\n"
                "- 0,25 = poco probable (1 de cada 4)\n"
                "- 0,50 = igual de probable (1 de cada 2)\n"
                "- 0,75 = muy probable (3 de cada 4)\n"
                "- 1,00 = seguro"
            )
        else:
            return (
                "✅ Ejemplo: 3 ÷ 10 = 0,3\n"
                "Esto significa que hay un 30% de probabilidad o que ocurre 3 de cada 10 veces."
            )

    # ────────── CONVERTIR A PORCENTAJE ──────────
    if hint_type == "stat_percent":
        if errors == 0:
            return (
                "👉 Multiplica el número decimal por 100 para transformarlo en porcentaje. "
                "Por ejemplo: 0,25 × 100 = 25%."
            )
        elif errors == 1:
            return (
                "🧮 El porcentaje indica cuántas veces ocurrirá de cada 100 intentos o personas. "
                "25% significa 25 de cada 100."
            )
        elif errors == 2:
            return (
                "💡 Conversión rápida:\n"
                "- 0,5 = 50% (mitad)\n"
                "- 0,25 = 25% (cuarto)\n"
                "- 0,75 = 75% (tres cuartos)\n"
                "- 0,1 = 10% (décima parte)"
            )
        else:
            return (
                "✅ Ejemplo completo:\n"
                "Probabilidad decimal: 0,3\n"
                "Porcentaje: 0,3 × 100 = 30%\n"
                "Interpretación: ocurrirá 30 de cada 100 veces."
            )

    # ────────── INTERPRETAR EL RESULTADO ──────────
    if hint_type == "stat_result" or hint_type == "data_resultado" or hint_type == "prob_resultado":
        if errors == 0:
            return (
                "👉 Piensa qué significa el resultado: 0,25 o 25% es una de cada cuatro veces. "
                "Compara con la realidad: ¿tiene sentido que sea tan probable o tan poco probable?"
            )
        elif errors == 1:
            return (
                "🧮 Ejemplo de interpretación:\n"
                "Si la probabilidad de lluvia es 0,8 (80%), es muy probable que llueva.\n"
                "Si es 0,1 (10%), es poco probable."
            )
        elif errors == 2:
            return (
                "💡 Contexto real:\n"
                "- En encuestas: 60% prefiere A, 40% prefiere B\n"
                "- En juegos: sacar 6 en un dado = 1/6 ≈ 16,7%\n"
                "- En deportes: probabilidad de ganar = 3/10 = 30%"
            )
        else:
            return (
                "✅ ¡Muy bien! Así interpretas probabilidades y porcentajes en gráficos o encuestas. "
                "Practica con ejemplos reales para dominar el concepto."
            )

    # ────────── EVENTOS Y CASOS ESPECÍFICOS ──────────
    if hint_type == "prob_evento":
        return (
            "👉 Identifica qué evento te están preguntando. "
            "Por ejemplo: '¿probabilidad de sacar un número par?' → eventos favorables: 2, 4, 6."
        )
    
    if hint_type == "prob_caso":
        return (
            "👉 Cuenta cuántos casos cumplen la condición y cuántos casos hay en total. "
            "Luego divide: casos favorables / total."
        )

    # ────────── FALLBACK ──────────
    return (
        "🤔 No tengo una pista específica para este paso, pero recuerda: "
        "compara los casos favorables con el total y piensa qué representa el resultado. 📊"
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
    "para estadística y probabilidad. No reveles la solución completa. "
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