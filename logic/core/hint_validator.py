# -*- coding: utf-8 -*-
"""
hint_validator.py
--------------------------------------------------
Valida que los hint_type usados por los motores existan
en el catálogo oficial de tipos definido en hint_types.json
"""

import json
import os

_HINTS_PATH = os.path.join(os.path.dirname(__file__), "hint_types.json")

try:
    with open(_HINTS_PATH, "r", encoding="utf-8") as f:
        _HINT_TYPES = json.load(f)
except Exception as e:
    print(f"[HINT_VALIDATOR] ⚠️ No se pudo cargar hint_types.json: {e}")
    _HINT_TYPES = {}


def is_valid_hint(topic: str, hint_type: str) -> bool:
    """
    Comprueba si un hint_type es válido para una materia o área dada.
    """
    topic = (topic or "").lower()
    hint_type = (hint_type or "").strip()

    if not topic or not hint_type:
        return False

    for area, sections in _HINT_TYPES.items():
        if topic == area.lower():
            for sub, hints in sections.items():
                if hint_type in hints:
                    return True
    return False
