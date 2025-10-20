# -*- coding: utf-8 -*-
"""
test_fractions.py
--------------------------------------------------
Prueba directa del motor de fracciones usando el sistema modular de Tutorín.
"""

import sys
import os

# Asegurar que el proyecto raíz esté en sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from logic.core.engine_loader import load_engine
from logic.core.engine_schema import validate_output


def probar_ejercicio(ejercicio, respuestas):
    print(f"\n🔹 Probando ejercicio: {ejercicio}")
    step_now = 0
    error_count = 0
    last_answer = ""

    engine_func = load_engine("fractions_engine")
    assert engine_func, "❌ No se pudo cargar fractions_engine"

    for i, resp in enumerate(respuestas, start=1):
        result = engine_func(ejercicio, step_now, last_answer, error_count)
        validate_output(result, "fractions_engine")

        print(f"\n➡️ Paso {step_now}:")
        print("🧠 Tutorín dice:", result["message"])
        print("Esperaba:", result.get("expected_answer"))

        last_answer = resp
        print(f"👦 Alumno responde: {last_answer}")

        # Avanzar paso
        step_now = result.get("next_step", step_now + 1)
        error_count = result.get("error_count", 0)

    # Resultado final
    result = engine_func(ejercicio, step_now, last_answer, error_count)
    print("\n✅ Resultado final:", result["message"])


# --- PRUEBAS DE EJEMPLO ---
if __name__ == "__main__":
    probar_ejercicio("2/3 + 1/3", ["3", "3", "3/3", "1/1"])
    probar_ejercicio("2/5 + 3/7", ["5 y 7", "35", "14", "15", "29", "29/35"])
