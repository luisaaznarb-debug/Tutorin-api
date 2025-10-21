import re
from typing import List

def _parse_mult(q: str):
    q2 = q.replace("Ã—", "*").replace("Â·", "*").replace("x", "*").replace("X", "*")
    m = re.search(r"^\s*(\d+)\s*\*\s*(\d+)\s*$", q2)
    if not m:
        return None
    a, b = int(m.group(1)), int(m.group(2))
    return a, b

def _compute_partials(a: int, b: int) -> List[int]:
    parts = []
    b_str = str(b)[::-1]  # derechaâ†’izquierda (unidades primero)
    for pos, ch in enumerate(b_str):
        d = int(ch)
        parts.append(a * d * (10 ** pos))  # ya viene desplazado
    return parts

def _width(a: int, b: int) -> int:
    total = a * b
    return max(len(str(a)), len(str(b)) + 2, len(str(total))) + 2

def _board(a: int, b: int, partials: List[int], upto_index: int, show_sum_line: bool) -> str:
    """Cabecera + lÃ­neas parciales ya confirmadas, monoespaciado."""
    w = _width(a, b)
    def rj(s: str) -> str: return s.rjust(w)
    lines = [
        rj(str(a)),
        rj("Ã— " + str(b)),
        rj("-" * max(len(str(a)), len(str(b)) + 2))
    ]
    for i in range(upto_index):
        lines.append(rj(str(partials[i])))
    if show_sum_line:
        lines.append(rj("-" * max(len(str(partials[-1])), len(str(partials[0])))))
    return "<pre style='font-family:monospace;line-height:1.25;margin:6px 0 0 0'>" + "\n".join(lines) + "</pre>"

def handle_step(question: str, step_now: int, last_answer: str, error_count: int):
    parsed = _parse_mult(question)
    if not parsed:
        return None
    a, b = parsed
    partials = _compute_partials(a, b)

    # Nueva estructura:
    # step 0 -> Pide directamente la lÃ­nea parcial #1 (unidades, SIN desplazar)
    # step 1..len(partials)-1 -> lÃ­neas parciales siguientes (ya desplazadas)
    # step len(partials) -> pide la suma final
    # > len(partials) -> done (sin revelar resultado)

    if step_now == 0:
        digit = int(str(b)[-1])  # unidades
        board = _board(a, b, partials, upto_index=0, show_sum_line=False)
        return {
            "status": "ask",
            "message": (
                f"{board}"
                f"ðŸ‘‰ Empezamos. Multiplica <b>{a}</b> por la <b>Ãºltima cifra</b> del nÃºmero de abajo, que es <b>{digit}</b>. "
                "Escribe el nÃºmero de esa <b>primera lÃ­nea parcial</b> (no hace falta desplazar)."
            ),
            "expected_answer": str(partials[0]),
            "topic": "multiplicacion",
            "hint_type": "mult_parcial"
        }

    # Pasos de lÃ­neas parciales siguientes
    if 1 <= step_now <= len(partials) - 1:
        idx = step_now  # 1..N-1 (pero es la lÃ­nea #idx+1)
        board = _board(a, b, partials, upto_index=idx, show_sum_line=False)
        digit_pos = idx  # 1=decenas, 2=centenas...
        digit = int(str(b)[::-1][digit_pos])
        return {
            "status": "ask",
            "message": (
                f"{board}"
                f"ðŸ‘‰ Calcula la <b>lÃ­nea parcial #{idx+1}</b>: multiplica <b>{a}</b> por la cifra <b>{digit}</b>. "
                "Como no es la cifra de las unidades, escribe el resultado <b>desplazado</b> (aÃ±ade ceros segÃºn la posiciÃ³n). "
                "Escribe solo el nÃºmero de esa lÃ­nea."
            ),
            "expected_answer": str(partials[digit_pos]),
            "topic": "multiplicacion",
            "hint_type": "mult_parcial"
        }

    # Ãšltimo paso: suma de parciales
    if step_now == len(partials):
        board = _board(a, b, partials, upto_index=len(partials), show_sum_line=True)
        total = a * b
        return {
            "status": "ask",
            "message": (
                f"{board}"
                "ðŸ‘‰ Ahora <b>suma en vertical</b> todas las lÃ­neas parciales para obtener el resultado final. "
                "Escribe solo el <b>resultado</b>."
            ),
            "expected_answer": str(total),
            "topic": "multiplicacion",
            "hint_type": "mult_suma_parciales"
        }

    if step_now > len(partials):
        return {
            "status": "done",
            "message": "Â¡Buen trabajo! Has completado todos los pasos de la multiplicaciÃ³n.",
            "expected_answer": "ok",
            "topic": "multiplicacion",
            "hint_type": "mult_suma_parciales"
        }

    # Fallback
    board = _board(a, b, partials, upto_index=0, show_sum_line=False)
    return {
        "status": "ask",
        "message": f"{board}Sigamos con la multiplicaciÃ³n.",
        "topic": "multiplicacion",
        "hint_type": "mult_parcial"
    }

# Compatibilidad
def handle_mult_step(question: str, step_now: int, last_answer: str, error_count: int):
    return handle_step(question, step_now, last_answer, error_count)