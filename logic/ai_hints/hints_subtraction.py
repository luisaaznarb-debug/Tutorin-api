from .hints_utils import _extract_pre_block, _first_int_on_line, _question

def _parse_sub_from_context(ctx: str):
    lines = _extract_pre_block(ctx).splitlines()
    if len(lines) < 2:
        return None
    a = _first_int_on_line(lines[0])
    b = _first_int_on_line(lines[1])
    if a is None or b is None:
        return None
    return (a, b)

def _sub_col_hint(context: str, err: int, cycle: str) -> str:
    parsed = _parse_sub_from_context(context)
    if parsed:
        a, b = parsed
        if err == 1:
            return f"👉 Resta {b} a {a}. Si no puedes, pide prestado. " + _question("¿Cuánto queda?")
        elif err == 2:
            return "🧮 Si pediste prestado, recuerda que equivale a 10 unidades. " + _question("¿Qué número queda?")
        elif err == 3:
            return "💡 Resta columna por columna y devuelve lo prestado si es necesario. " + _question("¿Cuál es la diferencia?")
        elif err >= 4:
            return f"✅ {a} − {b} = <b>{a - b}</b>."
    return "✅ Calcula y escribe el resultado correcto."
