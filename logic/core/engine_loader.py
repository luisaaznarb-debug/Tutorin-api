# -*- coding: utf-8 -*-
"""
engine_loader.py
--------------------------------------------------
Cargador dinámico de motores de Tutorín.

Compatible con:
 - handle_<engine>_step
 - handle_step
y búsqueda recursiva en logic/domains/*/
"""

import importlib
import os
import sys
from typing import Optional, Callable, Any

BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "domains"))
sys.path.append(BASE_PATH)


def load_engine(engine_name: str) -> Optional[Callable]:
    """
    Carga dinámicamente un motor según su nombre (ej: fractions_engine).
    """
    if not engine_name:
        print("[ENGINE_LOADER] ⚠️ Nombre de motor vacío.")
        return None

    try:
        for root, _, files in os.walk(BASE_PATH):
            for f in files:
                if f == f"{engine_name}.py":
                    # logic.domains.matematicas.fractions_engine
                    rel = os.path.relpath(os.path.join(root, f), start=os.path.dirname(__file__))
                    module_path = rel.replace(os.sep, ".").replace(".py", "").replace("..", "logic")

                    mod = importlib.import_module(module_path)

                    # 1️⃣ busca handle_<engine>_step
                    base_name = engine_name.split("_")[0]
                    func_name = f"handle_{base_name}_step"
                    func = getattr(mod, func_name, None)

                    # 2️⃣ si no existe, busca handle_step genérico
                    if not func:
                        func = getattr(mod, "handle_step", None)

                    # 3️⃣ si existe, retorna
                    if func:
                        print(f"[ENGINE_LOADER] ✅ Cargado: {module_path}.{func.__name__}")
                        return func

        print(f"[ENGINE_LOADER] ⚠️ Motor no encontrado: {engine_name}")
        return None

    except Exception as e:
        print(f"[ENGINE_LOADER] ❌ Error al cargar {engine_name}: {e}")
        return None


def available_engines() -> list[str]:
    """Devuelve lista de motores detectados."""
    engines = []
    for root, _, files in os.walk(BASE_PATH):
        for f in files:
            if f.endswith("_engine.py"):
                engines.append(f.replace(".py", ""))
    return sorted(engines)


def test_engine_load(engine_name: str) -> dict[str, Any]:
    """Prueba de diagnóstico manual."""
    func = load_engine(engine_name)
    if not func:
        return {"ok": False, "error": f"No se pudo cargar el motor '{engine_name}'."}
    try:
        result = func("2 + 3", 0, "", 0)
        return {"ok": True, "engine": engine_name, "result": result}
    except Exception as e:
        return {"ok": False, "error": str(e)}
