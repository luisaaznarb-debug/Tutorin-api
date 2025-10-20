# -*- coding: utf-8 -*-
"""
hints_decimals.py
--------------------------------------------------
Pistas educativas de Tutorín para operaciones con números decimales.
Formato coherente con el resto de motores y módulos de pistas.
"""

def get_hint(hint_type: str, errors: int = 0) -> str:
    """
    Devuelve una pista adaptada al tipo de paso (hint_type)
    y al número de errores acumulados.
    """

    hint_type = (hint_type or "").strip().lower()
    msg = ""

    # ---------------------------------------------------
    # INICIO / DETECCIÓN
    # ---------------------------------------------------
    if hint_type == "decimal_start":
        msg = (
            "🔍 Recuerda 😊 que los números con coma se llaman **decimales**. "
            "Por ejemplo, 3,2 significa tres enteros y dos décimas. "
            "Prueba a escribir una operación con decimales, como <code>2,5 + 1,4</code>."
        )

    elif hint_type == "decimal_identificar":
        msg = (
            "💡 Observa el signo que une los números: si es + es una **suma**, "
            "si es − una **resta**, si es × una **multiplicación** y si es ÷ una **división**. "
            "😉 Dime qué operación es esta."
        )

    # ---------------------------------------------------
    # ALINEAR COMAS
    # ---------------------------------------------------
    elif hint_type == "decimal_alinear":
        if errors == 0:
            msg = (
                "📏 Alinea las comas en vertical 😊 para que las unidades y décimas queden en la misma columna. "
                "Así podrás sumar o restar bien."
            )
        elif errors == 1:
            msg = (
                "🧮 Intenta escribir los números uno debajo del otro, "
                "de forma que las **comas estén alineadas**. ¡Eso te ayudará mucho! 😊"
            )
        else:
            msg = (
                "💭 Piensa: las comas deben quedar una debajo de otra 😉, "
                "porque cada cifra tiene que coincidir con su misma posición (unidades con unidades, décimas con décimas)."
            )

    # ---------------------------------------------------
    # OPERAR SIN COMA
    # ---------------------------------------------------
    elif hint_type == "decimal_operar":
        if errors == 0:
            msg = (
                "✏️ Puedes quitar la coma temporalmente para hacer la operación como si fueran enteros 😊. "
                "Luego la volveremos a poner al final 😉."
            )
        elif errors == 1:
            msg = (
                "💡 Si te cuesta, multiplica ambos números por 10 o 100 para quitar la coma, "
                "haz la operación y después **coloca la coma** según las cifras decimales totales."
            )
        else:
            msg = (
                "🔢 Recuerda 😊: quita la coma, haz la operación normal y al final vuelve a colocarla. "
                "Cuenta cuántas cifras había detrás de la coma entre los dos números."
            )

    # ---------------------------------------------------
    # RECOLOCAR COMA (RESULTADO FINAL)
    # ---------------------------------------------------
    elif hint_type == "decimal_resultado":
        if errors == 0:
            msg = (
                "🎯 Coloca la coma en el resultado para que tenga tantas cifras decimales "
                "como la suma de las cifras decimales de los números originales 😊."
            )
        elif errors == 1:
            msg = (
                "🤓 Cuenta cuántas cifras hay detrás de las comas en los números que has usado. "
                "Esa es la pista para saber dónde va la coma en el resultado 😉."
            )
        else:
            msg = (
                "🧠 Si ambos números tenían una cifra decimal, el resultado debe tener **dos cifras decimales**. "
                "Por ejemplo, 2,1 × 1,3 = 2,73 😊."
            )

    # ---------------------------------------------------
    # ERROR / DESCONOCIDO
    # ---------------------------------------------------
    elif hint_type == "decimal_error":
        msg = (
            "😅 Parece que algo no encaja. Intenta revisar la operación paso a paso. "
            "A veces ayuda escribir los números alineados y repasar la posición de la coma 😊."
        )

    # ---------------------------------------------------
    # FALLBACK (por si el hint_type no coincide)
    # ---------------------------------------------------
    else:
        msg = (
            "🤔 No pasa nada 😊. Recuerda: en las operaciones con decimales, "
            "las comas deben estar alineadas y el resultado debe tener la coma en el lugar correcto."
        )

    return msg
