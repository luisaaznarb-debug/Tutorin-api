# -*- coding: utf-8 -*-
"""
test_hints.py
--------------------------------------------------
Pruebas automáticas de los módulos de pistas de Tutorín.
"""

import os
import sys
import importlib
import pytest
import json

# Asegurar que Tutorín está en sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# === Paths base ===
HINTS_PATH = os.path.join("logic", "ai_hints")
HINT_TYPES_PATH = os.path.join("logic", "core", "hint_types.json")

# === Cargar tipos válidos ===
with open(HINT_TYPES_PATH, "r", encoding="utf-8") as f:
    HINT_TYPES = json.load(f)

# ---------------------------------------------------------------
# 🔍 UTILIDAD: listar todos los módulos de pistas disponibles
# ---------------------------------------------------------------
def list_hint_modules():
    """Lista todos los módulos de pistas, excluyendo hints_utils."""
    return sorted([
        f.replace(".py", "")
        for f in os.listdir(HINTS_PATH)
        if f.startswith("hints_")
        and f.endswith(".py")
        and f not in ["__init__.py", "hints_utils.py"]
    ])

# ---------------------------------------------------------------
# 🔧 TEST 1: comprobar que existen módulos de pistas
# ---------------------------------------------------------------
def test_hint_modules_exist():
    hints = list_hint_modules()
    assert hints, "No se encontraron módulos de pistas en logic/ai_hints/"
    print(f"\n📚 Módulos de pistas detectados: {hints}")

# ---------------------------------------------------------------
# 🔧 TEST 2: importar y comprobar que tienen función principal
# ---------------------------------------------------------------
@pytest.mark.parametrize("mod_name", list_hint_modules())
def test_hint_module_has_get_hint(mod_name):
    module_path = f"logic.ai_hints.{mod_name}"
    mod = importlib.import_module(module_path)

    has_get_hint = hasattr(mod, "get_hint")
    has_alt_func = any(fn for fn in dir(mod) if fn.startswith("_") and fn.endswith("_hint"))

    assert has_get_hint or has_alt_func, f"{mod_name} no tiene función get_hint() o equivalente"
    print(f"✅ {mod_name}: función de pista detectada.")

# ---------------------------------------------------------------
# 🔧 TEST 3: ejecutar get_hint() con ejemplos básicos
# ---------------------------------------------------------------
@pytest.mark.parametrize("mod_name", list_hint_modules())
def test_hint_outputs_are_valid(mod_name):
    module_path = f"logic.ai_hints.{mod_name}"
    mod = importlib.import_module(module_path)

    if hasattr(mod, "get_hint"):
        func = getattr(mod, "get_hint")
        hint_text = func("inicio", 0)
    else:
        hint_funcs = [getattr(mod, fn) for fn in dir(mod) if fn.endswith("_hint")]
        if not hint_funcs:
            pytest.skip(f"No hay función de pista en {mod_name}")
        func = hint_funcs[0]
        hint_text = func("Prueba de contexto", 0, "c2")

    assert isinstance(hint_text, str), f"{mod_name} no devuelve texto"
    assert len(hint_text.strip()) > 0, f"{mod_name} devuelve texto vacío"
    print(f"💬 {mod_name}: ejemplo de pista → {hint_text[:60]}...")

# ---------------------------------------------------------------
# 🔧 TEST 4: validar hint_types declarados
# ---------------------------------------------------------------
def test_hint_types_registered():
    """Verifica que hint_types.json esté correctamente estructurado."""
    for area, subareas in HINT_TYPES.items():
        assert isinstance(subareas, dict), f"{area} debe ser un dict"
        for sub, hints in subareas.items():
            assert isinstance(hints, list), f"{area}/{sub} debe ser una lista"
            assert hints, f"{area}/{sub} está vacío"
    print("✅ hint_types.json correctamente estructurado.")
