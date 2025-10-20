from .hints_utils import _extract_pre_block, _first_int_on_line, _question

def _parse_sum_from_context(ctx: str):
    lines = _extract_pre_block(ctx).splitlines()
    if len(lines) < 2:
        return None
    a = _first_int_on_line(lines[0])
    b = _first_int_on_line(lines[1])
    if a is None or b is None:
        return None
    return (a, b)

def _sum_col_hint(context: str, err: int, cycle: str) -> str:
    parsed = _parse_sum_from_context(context)
    if parsed:
        a, b = parsed
        if err == 1:
            return f"👉 Suma las unidades de {a} y {b}. " + _question("¿Cuánto te da?")
        elif err == 2:
            return "🧮 Si pasa de 9, lleva 1 a la siguiente columna. " + _question("¿Qué cifra escribes?")
        elif err == 3:
            return "💡 Suma cifra a cifra de derecha a izquierda. " + _question("¿Cuál es el resultado?")
        elif err >= 4:
            return f"✅ {a} + {b} = <b>{a + b}</b>."
    return "✅ Escribe la cifra correcta y continúa."
