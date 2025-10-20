from .hints_utils import _extract_pre_block, _question
import re

def _parse_div_from_context(ctx: str):
    txt = _extract_pre_block(ctx)
    m = re.search(r"(\d+)\s*[÷/:]\s*(\d+)", txt)
    if m:
        return int(m.group(1)), int(m.group(2))
    return None

def _division_hint(context: str, err: int, cycle: str) -> str:
    parsed = _parse_div_from_context(context)
    if parsed:
        a, d = parsed
        if err == 1:
            return f"👉 ¿Cuántas veces cabe {d} en {a}? " + _question("¿Qué número pones en el cociente?")
        elif err == 2:
            return "🧮 Multiplica el divisor por el cociente y réstalo. " + _question("¿Cuál es el resto?")
        elif err == 3:
            return "💡 Baja la siguiente cifra y repite. " + _question("¿Qué nueva cantidad divides?")
        elif err >= 4:
            q, r = divmod(a, d)
            return f"✅ {a} ÷ {d} = <b>{q}</b> (resto <b>{r}</b>)."
    return "✅ Completa la división correctamente."
