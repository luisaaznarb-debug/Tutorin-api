# -*- coding: utf-8 -*-
"""
test_motor_steps.py
--------------------------------------------------
Diagnóstico de motores de Tutorín:
- Carga cada motor
- Usa un ENUNCIADO ADECUADO para cada motor
- Verifica que devuelve next_step > step_now
- Detecta repeticiones y finalización
"""

import os
import sys

# ---- Configuración de rutas (raíz del proyecto) ----
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from logic.core.engine_loader import load_engine, available_engines

# ---- Enunciado de ejemplo por motor ----
SAMPLE_PROMPTS = {
    "addition_engine":        "32458 + 6541",
    "subtraction_engine":     "32458 - 6541",
    "multiplication_engine":  "32547 * 23",        # también acepta '×' si tu motor lo soporta
    "division_engine":        "32547 / 52",        # también acepta '÷' si tu motor lo soporta
    "fractions_engine":       "5/6 + 4/8",
    "decimals_engine":        "5,2 + 3,0"          # o "5.2 + 3.0" según motor
}

print("\n🔍 Motores detectados:", available_engines(), "\n")

def test_motor(engine_name: str):
    print(f"🧩 Probando motor: {engine_name}")
    func = load_engine(engine_name)
    if not func:
        print(f"❌ No se pudo cargar el motor {engine_name}\n")
        return

    prompt = SAMPLE_PROMPTS.get(engine_name, "2 + 3")
    step = 0
    last_answer = ""
    error_count = 0
    max_cycles = 10
    seen_steps = set()

    try:
        for i in range(max_cycles):
            result = func(prompt, step, last_answer, error_count)

            if not isinstance(result, dict):
                print(f"❌ {engine_name}: resultado no es un dict → {type(result)}\n")
                return

            status = result.get("status", "ask")
            next_step = result.get("next_step", step)
            msg = result.get("message", "")
            expected = result.get("expected_answer", "")

            print(f"   Paso {step} → {next_step} | Estado: {status} | Esperado: {expected}")
            if msg:
                recorte = (msg[:80] + "...") if len(msg) > 80 else msg
                print(f"   Mensaje: {recorte}")

            if next_step == step:
                print(f"⚠️  {engine_name}: repite el paso {step}, revisar 'next_step'\n")
                return

            if step in seen_steps:
                print(f"⚠️  {engine_name}: ciclo detectado en paso {step}\n")
                return

            seen_steps.add(step)
            step = next_step
            last_answer = str(expected)

            if status == "done":
                print(f"✅  {engine_name}: completado correctamente en paso {step}\n")
                return

        print(f"⚠️  {engine_name}: no completó en {max_cycles} pasos\n")

    except Exception as e:
        print(f"❌ Error en {engine_name}: {e}\n")


if __name__ == "__main__":
    for eng in available_engines():
        test_motor(eng)
