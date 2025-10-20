# -*- coding: utf-8 -*-
"""
test_motors.py
--------------------------------------------------
Pruebas automáticas de todos los motores de Tutorín.

✅ Comprueba:
- Que todos los motores definidos en nlu_labels.json existen.
- Que cada motor se carga dinámicamente sin errores.
- Que devuelven una salida compatible con ENGINE_OUTPUT_SCHEMA.
"""

import os
import sys
import json
import pytest

# Asegurar que el proyecto está en sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from logic.core.engine_loader import available_engines, load_engine
from logic.core.engine_schema import validate_output

# === CARGAR CONFIGURACIÓN DE MOTORES DESDE nlu_labels.json ===
LABELS_PATH = os.path.join("modules", "nlu_labels.json")
with open(LABELS_PATH, "r", encoding="utf-8") as f:
    LABELS = json.load(f)


# ---------------------------------------------------------------
# 🔍 UTILIDAD: listar todos los motores declarados en el sistema
# ---------------------------------------------------------------
def declared_engines():
    engines = []
    for subject, data in LABELS.items():
        if "engines" in data:
            for name, engine in data["engines"].items():
                engines.append(engine)
    return sorted(list(set(engines)))


# ---------------------------------------------------------------
# 🔧 TEST 1: comprobar que todos los motores existen
# ---------------------------------------------------------------
def test_all_engines_exist():
    declared = declared_engines()
    available = available_engines()
    missing = [e for e in declared if e not in available]
    print("\n🧩 Motores declarados:", declared)
    print("🧠 Motores disponibles:", available)
    assert not missing, f"Faltan los motores: {missing}"


# ---------------------------------------------------------------
# 🔧 TEST 2: cargar y ejecutar todos los motores
# ---------------------------------------------------------------
@pytest.mark.parametrize("engine_name", declared_engines())
def test_engine_runs(engine_name):
    func = load_engine(engine_name)
    assert func is not None, f"No se pudo cargar {engine_name}"

    try:
        result = func("2 + 3", 0, "", 0)
        assert isinstance(result, dict), f"{engine_name} no devolvió un dict"
        assert validate_output(result, engine_name), f"{engine_name} no cumple el formato"
    except Exception as e:
        pytest.fail(f"{engine_name} falló al ejecutarse: {e}")


# ---------------------------------------------------------------
# 🔧 TEST 3: comprobar que los motores devuelven hint_types válidos
# ---------------------------------------------------------------
from logic.core.hint_validator import is_valid_hint

@pytest.mark.parametrize("engine_name", declared_engines())
def test_hint_type_is_valid(engine_name):
    func = load_engine(engine_name)
    if not func:
        pytest.skip(f"No se pudo cargar {engine_name}")
    result = func("3 + 5", 0, "", 0)
    topic = result.get("topic", "")
    hint = result.get("hint_type", "")
    assert is_valid_hint(topic, hint), f"{engine_name}: hint_type '{hint}' no es válido para '{topic}'"
