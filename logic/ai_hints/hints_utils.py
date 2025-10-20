# Funciones auxiliares compartidas por todos los módulos de pistas

import re, math

def _question(fmt: str) -> str:
    q = fmt.strip()
    return q if q.endswith("?") else q + "?"

def _extract_pre_block(context: str) -> str:
    if not context:
        return ""
    m = re.search(r"<pre[^>]*>(.*?)</pre>", context, re.S | re.I)
    return (m.group(1) if m else context).strip()

def _first_int_on_line(line: str):
    m = re.search(r"(-?\d+)", line)
    return int(m.group(1)) if m else None

def _lcm(a: int, b: int) -> int:
    return abs(a * b) // math.gcd(a, b) if a and b else 0
