from .hints_utils import _extract_pre_block, _question, _first_int_on_line

def _parse_mult_from_context(ctx: str):
    lines = _extract_pre_block(ctx).splitlines()
    if len(lines) < 2:
        return None
    a = _first_int_on_line(lines[0])
    b = _first_int_on_line(lines[1])
    if a is None or b is None:
        return None
    return (a, b)

def _mult_parcial_hint(context: str, err: int, cycle: str) -> str:
    parsed = _parse_mult_from_context(context)
    if parsed:
        a, b = parsed
        if err == 1:
            return f"👉 Multiplica {a} × {b}. " + _question("¿Cuál es el resultado parcial?")
        elif err == 2:
            return "🧮 Escribe el resultado desplazado según la posición. " + _question("¿Qué número obtienes?")
        elif err == 3:
            return "💡 Suma todas las líneas parciales. " + _question("¿Qué total obtienes?")
        elif err >= 4:
            return f"✅ {a} × {b} = <b>{a * b}</b>."
    return "✅ Escribe la línea parcial correcta y continúa."
