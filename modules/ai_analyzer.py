# -*- coding: utf-8 -*-
"""
ai_analyzer.py
--------------------------------------------------
Analiza lo que el niño escribe o dice y decide:
- subject (materia)
- intent (tipo de tarea)
- engine (motor a invocar)
Luego usa el núcleo de Tutorín (engine_loader + BaseEngine)
para ejecutar el motor correspondiente.
"""

import json
import os
import re
from typing import Dict, Any

# === IMPORTAR EL NUEVO NÚCLEO ===
from logic.core.engine_loader import load_engine
from logic.core.engine_schema import validate_output

# === CARGA DE PALABRAS CLAVE ===
_BASE = os.path.dirname(os.path.abspath(__file__))
_LABELS_PATH = os.path.join(_BASE, "nlu_labels.json")


def _load_labels() -> Dict[str, Any]:
    """Carga las palabras clave desde nlu_labels.json"""
    try:
        with open(_LABELS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[AI_ANALYZER] ⚠️ No se pudo cargar nlu_labels.json: {e}")
        return {}


_LABELS = _load_labels()

# === PATRONES DIRECTOS (detección rápida) ===
_REGEX_RULES = [
    (r"\d+\s*/\s*\d+\s*[\+\-]\s*\d+(?:\s*/\s*\d+)?", ("matematicas", "fracciones", "fractions_engine")),
    (r"\d+\s*(?:÷|:|/)\s*\d+", ("matematicas", "division", "division_engine")),
    (r"\d+\s*(?:×|\*|x|X|·)\s*\d+", ("matematicas", "multiplicacion", "multiplication_engine")),
    (r"\d+\s*\+\s*\d+", ("matematicas", "suma", "addition_engine")),
    (r"\d+\s*\-\s*\d+", ("matematicas", "resta", "subtraction_engine")),
    (r"\d+[.,]\d+\s*([+\-×x*/:])\s*\d+[.,]\d+", ("matematicas", "decimales", "decimals_engine")),
    (r"\d+\s*%\s*\d+", ("matematicas", "porcentajes", "percentages_engine"))
]


# ================================================================
# 🧠 FUNCIÓN PRINCIPAL: ANALIZAR EL PROMPT
# ================================================================
def analyze_prompt(prompt: str) -> Dict[str, Any]:
    """
    Detecta la materia, el tipo de operación (intent) y el motor asociado.
    Devuelve un diccionario con subject, intent, engine y confidence.
    """
    text = (prompt or "").strip().lower()
    if not text:
        return {"subject": "general", "intent": "vacío", "engine": None, "confidence": 0.0}

    # --- 1️⃣ Reglas directas (regex) ---
    for pattern, out in _REGEX_RULES:
        if re.search(pattern, text):
            subject, intent, engine = out
            return {"subject": subject, "intent": intent, "engine": engine, "confidence": 0.95}

    # --- 2️⃣ Palabras clave desde nlu_labels ---
    for subject, cfg in _LABELS.items():
        palabras = cfg.get("palabras_clave", [])
        engines = cfg.get("engines", {})

        for intent, engine in engines.items():
            tokens = [intent] + palabras
            if any(tok in text for tok in tokens):
                return {"subject": subject, "intent": intent, "engine": engine, "confidence": 0.75}

    # --- 3️⃣ Fallback ---
    return {"subject": "general", "intent": "desconocido", "engine": None, "confidence": 0.3}


# ================================================================
# ⚙️ EJECUTAR MOTOR DETECTADO
# ================================================================
def run_engine_for(engine_name: str, prompt: str, step: int, answer: str, errors: int) -> Dict[str, Any]:
    """
    Carga y ejecuta el motor correspondiente usando el sistema dinámico.
    """
    if not engine_name:
        return {
            "status": "ask",
            "message": "No sé exactamente qué tipo de ejercicio es. ¿Podrías explicarlo un poco más?",
            "expected_answer": None,
            "topic": "general",
            "hint_type": "general_indefinido",
            "next_step": step
        }

    # --- 1️⃣ Cargar el motor dinámicamente ---
    engine_func = load_engine(engine_name)
    if not engine_func:
        return {
            "status": "error",
            "message": f"No se pudo encontrar el motor '{engine_name}'.",
            "expected_answer": None,
            "topic": "general",
            "hint_type": "general_error",
            "next_step": step
        }

    # --- 2️⃣ Ejecutar el motor ---
    try:
        result = engine_func(prompt, step, answer, errors)
        validate_output(result, engine_name)
        return result
    except Exception as e:
        print(f"[AI_ANALYZER] ❌ Error en motor {engine_name}: {e}")
        return {
            "status": "error",
            "message": f"Se produjo un error en el motor {engine_name}: {str(e)}",
            "expected_answer": None,
            "topic": "general",
            "hint_type": "general_error",
            "next_step": step
        }


# ================================================================
# 🧪 DIAGNÓSTICO
# ================================================================
def test_analyzer():
    """
    Prueba rápida del analizador y de la carga dinámica de motores.
    """
    examples = [
        "3 + 5",
        "2,5 + 1,25",
        "25% de 80",
        "4/6 + 1/3",
        "dividir 24 entre 6"
    ]

    for ex in examples:
        info = analyze_prompt(ex)
        print("\n🧩", ex)
        print("→", info)

        engine_name = info["engine"]
        if engine_name:
            res = run_engine_for(engine_name, ex, 0, "", 0)
            print("⚙️ Resultado:", res)
        else:
            print("❌ No se detectó motor.")
