# -*- coding: utf-8 -*-
"""
hints_decimals.py
Pistas progresivas para decimales según nivel de error.
Compatible con decimals_engine.py
"""

from typing import Optional

# ────────── Pistas por nivel ──────────
def get_hint(hint_type: str, errors: int = 0) -> str:
    """
    Devuelve una pista adaptada al tipo de paso y número de errores.
    
    Args:
        hint_type: tipo de paso ('decimal_start', 'decimal_identificar', etc.)
        errors: nivel de error (0-4+)
    """
    hint_type = (hint_type or "").strip().lower()
    errors = max(0, min(int(errors or 0), 4))

    # ────────── INICIO / DETECCIÓN ──────────
    if hint_type == "decimal_start":
        if errors == 0:
            return (
                "🔍 Recuerda que los números con coma se llaman <b>decimales</b>. "
                "Por ejemplo, 3,2 significa tres enteros y dos décimas."
            )
        elif errors == 1:
            return (
                "💡 Prueba a escribir una operación con decimales, "
                "como <code>2,5 + 1,4</code> o <code>3,2 × 1,5</code>."
            )
        else:
            return (
                "✅ Los decimales se escriben con coma (en España) o punto (en otros países). "
                "La parte antes de la coma son los <b>enteros</b>, y la parte después son las <b>décimas, centésimas</b>..."
            )

    if hint_type == "decimal_identificar":
        if errors == 0:
            return (
                "👉 Observa el signo que une los números: "
                "si es + es una <b>suma</b>, si es − una <b>resta</b>, "
                "si es × una <b>multiplicación</b> y si es ÷ una <b>división</b>."
            )
        elif errors == 1:
            return "🧮 Fíjate bien en el símbolo entre los dos números. " + _question("¿Qué operación es?")
        else:
            return (
                "💡 Los símbolos matemáticos son: + (suma), − (resta), × (multiplicación), ÷ (división). "
                "Identifica cuál aparece en tu operación."
            )

    # ────────── ALINEAR COMAS ──────────
    if hint_type == "decimal_alinear":
        if errors == 0:
            return (
                "📏 Alinea las <b>comas en vertical</b> para que las unidades y décimas "
                "queden en la misma columna. Así podrás sumar o restar bien."
            )
        elif errors == 1:
            return (
                "🧮 Escribe los números uno debajo del otro, "
                "de forma que las <b>comas estén alineadas</b>. ¡Eso te ayudará mucho!"
            )
        elif errors == 2:
            return (
                "💡 Ejemplo: si tienes 3,25 + 1,4, escríbelo así:\n"
                "<pre>  3,25\n+ 1,40\n------</pre>\n"
                "Las comas deben quedar una debajo de otra."
            )
        else:
            return (
                "✅ Recuerda: las comas deben quedar una debajo de otra, "
                "porque cada cifra tiene que coincidir con su misma posición "
                "(unidades con unidades, décimas con décimas)."
            )

    # ────────── OPERAR SIN COMA ──────────
    if hint_type == "decimal_operar":
        if errors == 0:
            return (
                "✏️ Puedes quitar la coma temporalmente para hacer la operación "
                "como si fueran enteros. Luego la volveremos a poner al final."
            )
        elif errors == 1:
            return (
                "💡 Si te cuesta, multiplica ambos números por 10 o 100 para quitar la coma, "
                "haz la operación y después <b>coloca la coma</b> según las cifras decimales totales."
            )
        elif errors == 2:
            return (
                "🧮 Ejemplo: 2,3 × 1,5 → quita las comas: 23 × 15 = 345. "
                "Luego cuenta: había 1 decimal en 2,3 y 1 decimal en 1,5 = 2 decimales en total. "
                "Resultado: 3,45."
            )
        else:
            return (
                "✅ Recuerda: quita la coma, haz la operación normal y al final vuelve a colocarla. "
                "Cuenta cuántas cifras había detrás de la coma entre los dos números."
            )

    # ────────── RECOLOCAR COMA (RESULTADO FINAL) ──────────
    if hint_type == "decimal_resultado":
        if errors == 0:
            return (
                "🎯 Coloca la coma en el resultado para que tenga tantas cifras decimales "
                "como la suma de las cifras decimales de los números originales."
            )
        elif errors == 1:
            return (
                "🤓 Cuenta cuántas cifras hay detrás de las comas en los números que has usado. "
                "Esa es la pista para saber dónde va la coma en el resultado."
            )
        elif errors == 2:
            return (
                "💡 Si ambos números tenían una cifra decimal, el resultado debe tener "
                "<b>dos cifras decimales</b>. Por ejemplo, 2,1 × 1,3 = 2,73."
            )
        else:
            return (
                "✅ Muy bien. Ejemplo completo:\n"
                "3,2 × 1,5: quitamos comas → 32 × 15 = 480.\n"
                "Contamos decimales: 1 + 1 = 2 decimales.\n"
                "Resultado: 4,80 (o 4,8)."
            )

    # ────────── ERROR / DESCONOCIDO ──────────
    if hint_type == "decimal_error":
        return (
            "😅 Parece que algo no encaja. Intenta revisar la operación paso a paso. "
            "A veces ayuda escribir los números alineados y repasar la posición de la coma."
        )

    # ────────── FALLBACK ──────────
    return (
        "🤔 Recuerda: en las operaciones con decimales, "
        "las comas deben estar alineadas y el resultado debe tener la coma en el lugar correcto."
    )

# ────────── Utilidad auxiliar ──────────
def _question(text: str) -> str:
    """Asegura que termine en interrogación."""
    t = text.strip()
    return t if t.endswith("?") else t + "?"

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
    "para operaciones con decimales. No reveles la solución completa. "
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