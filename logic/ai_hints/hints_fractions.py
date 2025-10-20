from .hints_utils import _extract_pre_block, _lcm, _question
import re, math

# ──────────────────────────────────────────────────────────────
# AUX: leer dos fracciones A/B (op) C/D desde el contexto
# ──────────────────────────────────────────────────────────────
def _parse_two_fractions(ctx: str):
    text = ctx or ""

    # Marcador oculto
    m = re.search(r"\[FRAC:\s*(\d+)\s*/\s*(\d+)\s*([+\-])\s*(\d+)\s*/\s*(\d+)\s*\]", text)
    if m:
        a, b, op, c, d = int(m.group(1)), int(m.group(2)), m.group(3), int(m.group(4)), int(m.group(5))
        return ((a, b), (c, d), op)

    # Desde el <pre>
    pre = _extract_pre_block(text) or ""
    m = re.search(r"(\d+)\s*/\s*(\d+)\s*([+\-])\s*(\d+)\s*/\s*(\d+)", pre)
    if m:
        a, b, op, c, d = int(m.group(1)), int(m.group(2)), m.group(3), int(m.group(4)), int(m.group(5))
        return ((a, b), (c, d), op)

    # Fallback
    m = re.search(r"(\d+)\s*/\s*(\d+)\s*([+\-])\s*(\d+)\s*/\s*(\d+)", text)
    if m:
        a, b, op, c, d = int(m.group(1)), int(m.group(2)), m.group(3), int(m.group(4)), int(m.group(5))
        return ((a, b), (c, d), op)

    return None

# ──────────────────────────────────────────────────────────────
# 0️⃣ INICIO (sí/no)
# ──────────────────────────────────────────────────────────────
def _frac_inicio_hint(context: str, err: int, cycle: str) -> str:
    pf = _parse_two_fractions(context)
    if pf:
        (a,b),(c,d),_ = pf
        correcta = "sí" if b == d else "no"
    else:
        b, d, correcta = 3, 5, "no"

    if err == 1:
        return "👉 Fíjate bien: el <b>denominador</b> es el número de <b>abajo</b> en cada fracción. " + _question("¿Son iguales?")
    elif err == 2:
        return f"🧮 Mira sólo los de abajo: {b} y {d}. " + _question("¿Coinciden?")
    elif err == 3:
        return f"📘 Denominadores vistos: {b} y {d}. Si son iguales, responde 'sí'; si no, responde 'no'."
    else:
        return f"✅ Respuesta correcta: <b>{correcta}</b>."

# ──────────────────────────────────────────────────────────────
# 1️⃣ MCM
# ──────────────────────────────────────────────────────────────
def _frac_mcm_hint(context: str, err: int, cycle: str) -> str:
    pf = _parse_two_fractions(context)
    if pf:
        (a,b),(c,d),_ = pf
    else:
        b, d = 3, 5
    m = _lcm(b, d)
    if err == 1:
        return f"👉 El m.c.m. es el primer múltiplo común de {b} y {d}. " + _question("¿Cuál te sale?")
    elif err == 2:
        return f"🧮 Escribe los múltiplos de {b} y {d} y encuentra el primero común. " + _question("¿Cuál coincide?")
    elif err == 3:
        multiples_b = ', '.join(str(b*i) for i in range(1,7))
        multiples_d = ', '.join(str(d*i) for i in range(1,7))
        return f"📘 Múltiplos de {b}: {multiples_b}\nMúltiplos de {d}: {multiples_d}\n" + _question("¿Cuál es el primer número que coincide?")
    else:
        return f"✅ El m.c.m.({b},{d}) = <b>{m}</b>."

# ──────────────────────────────────────────────────────────────
# 2️⃣ FRACCIONES EQUIVALENTES
# ──────────────────────────────────────────────────────────────
def _frac_equiv_hint(context: str, err: int, cycle: str) -> str:
    pf = _parse_two_fractions(context)
    if not pf:
        return "👉 Convierte ambas fracciones al mismo denominador."
    (a,b),(c,d),_ = pf
    m = _lcm(b, d)
    kb, kd = (m // b), (m // d)
    A, C = a * kb, c * kd

    if err == 1:
        return (f"👉 Tienes que multiplicar el <b>numerador</b> por el <b>mismo número</b> "
                f"que has multiplicado el denominador para obtener {m}. "
                f"¿Qué números obtienes? Dímelos separados por 'y' (ej.: {A} y {C}).")
    elif err == 2:
        return (f"🧮 En la primera fracción has multiplicado el denominador por <b>{kb}</b>, "
                f"y en la segunda por <b>{kd}</b>. "
                f"Multiplica el numerador por la misma cifra en cada fracción. "
                f"¿Qué números te salen? Dímelos separados por 'y' (ej.: {A} y {C}).")
    elif err == 3:
        return (f"📘 Así queda: {a}/{b} → ({a}×{kb})/({b}×{kb}) = <b>{A}/{m}</b>, "
                f"y {c}/{d} → ({c}×{kd})/({d}×{kd}) = <b>{C}/{m}</b>. "
                f"¿Qué numeradores obtienes?")
    else:
        return (f"✅ Perfecto. Fracciones equivalentes: <b>{A}/{m}</b> y <b>{C}/{m}</b>. "
                f"(Numeradores nuevos: <b>{A} y {C}</b>)")

# ──────────────────────────────────────────────────────────────
# 3️⃣ OPERACIÓN
# ──────────────────────────────────────────────────────────────
def _frac_operacion_hint(context: str, err: int, cycle: str) -> str:
    pf = _parse_two_fractions(context)
    if not pf:
        return "👉 Opera los numeradores y conserva el denominador común."
    (a,b),(c,d),op = pf
    m = _lcm(b, d)
    kb, kd = m//b, m//d
    a2, c2 = a*kb, c*kd
    num = a2 + c2 if op == "+" else a2 - c2

    if err == 1:
        return f"👉 Ya tienen denominador común ({m}). Opera <b>sólo</b> los numeradores: {a2} {op} {c2}. " + _question("¿Qué obtienes?")
    elif err == 2:
        return f"🧮 El denominador queda igual ({m}). Calcula: {a2} {op} {c2}. " + _question("¿Cuál es el numerador resultante?")
    elif err == 3:
        return f"📘 {a2}{op}{c2} = <b>{num}</b>. Resultado parcial: <b>{num}/{m}</b>."
    else:
        return f"✅ {a}/{b} {op} {c}/{d} = <b>{num}/{m}</b> (sin simplificar)."

# ──────────────────────────────────────────────────────────────
# 4️⃣ SIMPLIFICAR
# ──────────────────────────────────────────────────────────────
def _frac_simplificar_hint(context: str, err: int, cycle: str) -> str:
    m = re.search(r"\[FRAC:\s*(\d+)\s*/\s*(\d+)\s*([+\-])\s*(\d+)\s*/\s*(\d+)\s*\]", context or "")
    if m:
        a, b, op, c, d = int(m.group(1)), int(m.group(2)), m.group(3), int(m.group(4)), int(m.group(5))
        mcm = _lcm(b, d)
        kb, kd = mcm // b, mcm // d
        A, C = a * kb, c * kd
        n = A + C if op == "+" else A - C
        den = mcm
        g = math.gcd(n, den)
    else:
        txt = _extract_pre_block(context) or ""
        all_fracs = re.findall(r"(\d+)\s*/\s*(\d+)", txt)
        if not all_fracs:
            n, den, g = 32, 24, math.gcd(32, 24)
        else:
            n, den = map(int, all_fracs[-1])
            g = math.gcd(n, den)

    # Siempre calcula g con la fracción actual
    g = math.gcd(n, den)

    
    # ⬇️ IMPORTANTE: añade el marcador en TODAS las pistas para que persista
    marker = f"<span style='display:none'>[GCD:{g}]</span>"

    if g == 1:
        return f"✅ No se puede simplificar más, ya que {n} y {den} no tienen divisores comunes."

    if err == 1:
        print("DEBUG:", err, context)
        return (f"👉 Busca un número mayor que 1 que divida tanto a {n} como a {den}. "
                + _question("¿Qué número puedes usar como divisor común?")
                + marker)
    elif err == 2:
        return (f"🧮 Divide el numerador y el denominador por ese número común (por ejemplo, {g}). "
                + _question("¿Qué fracción obtienes después de dividir?")
                + marker)
    elif err == 3:
        return (f"📘 Vamos juntos: {n} ÷ {g} = {n//g} y {den} ÷ {g} = {den//g}. "
                + _question("¿Cuál es la fracción simplificada?")
                + marker)
    else:
        return (f"✅ Muy bien. {n}/{den} ÷ {g}/{g} = <b>{n//g}/{den//g}</b>. "
                f"Esa es la fracción simplificada.")
