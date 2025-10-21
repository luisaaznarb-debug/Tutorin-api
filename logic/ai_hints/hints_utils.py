# -*- coding: utf-8 -*-
"""
hints_utils.py
Funciones auxiliares compartidas por todos los módulos de pistas.
"""

import re
import math

def _question(fmt: str) -> str:
    """Asegura que una frase termine en interrogación."""
    q = fmt.strip()
    return q if q.endswith("?") else q + "?"

def _extract_pre_block(context: str) -> str:
    """Extrae el contenido de un bloque <pre>...</pre>."""
    if not context:
        return ""
    m = re.search(r"<pre[^>]*>(.*?)</pre>", context, re.S | re.I)
    return (m.group(1) if m else context).strip()

def _first_int_on_line(line: str):
    """Encuentra el primer número entero en una línea."""
    m = re.search(r"(-?\d+)", line)
    return int(m.group(1)) if m else None

def _lcm(a: int, b: int) -> int:
    """Calcula el mínimo común múltiplo."""
    return abs(a * b) // math.gcd(a, b) if a and b else 0

def _sanitize(text: str) -> str:
    """Limpia marcado matemático y formato del texto."""
    if not text:
        return text
    t = re.sub(r"\$[^$]*\$", " ", text)
    t = re.sub(r"\\\(|\\\)|\\\[|\\\]", " ", t)
    t = re.sub(r"\\frac\s*\{(\d+)\}\s*\{(\d+)\}", r"\1/\2", t)
    t = re.sub(r"\\times", "×", t)
    t = re.sub(r"\*\*(.*?)\*\*", r"\1", t)
    t = re.sub(r"`([^`]*)`", r"\1", t)
    t = re.sub(r"\s{2,}", " ", t).strip()
    return t

def format_hint_message(text: str) -> str:
    """Formatea un mensaje de pista con estructura clara."""
    return text.strip()