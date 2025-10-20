# -*- coding: utf-8 -*-
"""
engine_schema.py
--------------------------------------------------
Define el formato estándar de salida de los motores de Tutorín
y funciones para validar que todos lo cumplen correctamente.
También verifica que los hint_type devueltos por los motores
están registrados en hint_types.json mediante hint_validator.py.
"""

from typing import Any, Dict
from .hint_validator import is_valid_hint

# -------------------------------------------------------
# 📘 FORMATO ESTÁNDAR DE SALIDA
# -------------------------------------------------------

ENGINE_OUTPUT_SCHEMA: Dict[str, Any] = {
    "status": str,             # Estado del motor: "ask", "done", "feedback", "error"...
    "message": str,            # Texto o HTML educativo mostrado al alumno
    "expected_answer": (str, type(None)),  # Respuesta esperada o None si no aplica
    "topic": str,              # Materia o ámbito ("matematicas", "lengua", "decimales"...)
    "hint_type": str,          # Tipo de pista que usará ai_router
    "next_step": int           # Número del siguiente paso (0 o superior)
}


# -------------------------------------------------------
# 🧩 FUNCIÓN DE VALIDACIÓN
# -------------------------------------------------------

def validate_output(data: Dict[str, Any], engine_name: str = "unknown") -> bool:
    """
    Valida que un motor devuelva todos los campos requeridos y del tipo correcto.
    También valida que el hint_type esté registrado en hint_types.json.
    Retorna True si es válido, False si hay errores.
    """
    if not isinstance(data, dict):
        print(f"[ENGINE_SCHEMA] ❌ {engine_name}: el resultado no es un dict.")
        return False

    valid = True

    # 1️⃣ Validar estructura básica
    for key, expected_type in ENGINE_OUTPUT_SCHEMA.items():
        if key not in data:
            print(f"[ENGINE_SCHEMA] ⚠️ {engine_name}: falta el campo '{key}'.")
            valid = False
            continue

        val = data[key]
        if isinstance(expected_type, tuple):
            if not isinstance(val, expected_type):
                print(f"[ENGINE_SCHEMA] ⚠️ {engine_name}: '{key}' tiene tipo {type(val).__name__}, esperado uno de {expected_type}.")
                valid = False
        else:
            if not isinstance(val, expected_type):
                print(f"[ENGINE_SCHEMA] ⚠️ {engine_name}: '{key}' tiene tipo {type(val).__name__}, esperado {expected_type.__name__}.")
                valid = False

    # 2️⃣ Validar hint_type (solo si los campos existen)
    topic = data.get("topic", "")
    hint = data.get("hint_type", "")
    if topic and hint:
        if not is_valid_hint(topic, hint):
            print(f"[ENGINE_SCHEMA] ⚠️ {engine_name}: hint_type desconocido '{hint}' para tema '{topic}'.")
            valid = False
    else:
        print(f"[ENGINE_SCHEMA] ⚠️ {engine_name}: faltan campos 'topic' o 'hint_type' para validación semántica.")
        valid = False

    if valid:
        print(f"[ENGINE_SCHEMA] ✅ {engine_name}: formato y hint_type correctos.")
    return valid


# -------------------------------------------------------
# 🧪 UTILIDAD DE PRUEBA
# -------------------------------------------------------

def test_engine_schema(func) -> None:
    """
    Ejecuta un motor y valida su salida.
    Ejemplo:
        >>> from logic.core.engine_loader import load_engine
        >>> f = load_engine("decimals_engine")
        >>> test_engine_schema(f)
    """
    try:
        result = func("2 + 3", 0, "", 0)
        validate_output(result, func.__name__)
    except Exception as e:
        print(f"[ENGINE_SCHEMA] ❌ Error ejecutando motor {func}: {e}")
