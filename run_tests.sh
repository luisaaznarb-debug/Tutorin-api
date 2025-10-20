#!/bin/bash
# ==========================================================
# 🧪 Tutorín — Test Suite Automático
# ----------------------------------------------------------
# Ejecuta todas las pruebas del backend de Tutorín:
#   1️⃣ Validación de motores (formato + hint_type + carga dinámica)
#   2️⃣ Validación de pistas (funciones + coherencia de salida)
# ==========================================================

clear
echo "🧩=============================================================="
echo "🧠   TUTORÍN — SISTEMA AUTOMÁTICO DE VALIDACIÓN"
echo "🧩=============================================================="
echo ""

# Comprobar si pytest está instalado
if ! command -v pytest &> /dev/null
then
    echo "⚠️  pytest no está instalado. Ejecuta:"
    echo "   pip install pytest"
    exit 1
fi

# Ejecutar pruebas de motores
echo "🔧 [1/2] Probando motores..."
pytest tests/test_motors.py -v --maxfail=1 --disable-warnings
motors_exit=$?
echo ""

# Ejecutar pruebas de pistas
echo "💬 [2/2] Probando pistas..."
pytest tests/test_hints.py -v --maxfail=1 --disable-warnings
hints_exit=$?
echo ""

# Resultado final
if [ $motors_exit -eq 0 ] && [ $hints_exit -eq 0 ]; then
    echo "✅✅✅  Todas las pruebas de Tutorín se ejecutaron correctamente ✅✅✅"
    echo "🌈 El sistema está estable y listo para continuar con el desarrollo."
    exit 0
else
    echo "❌❌❌  Se detectaron errores en las pruebas ❌❌❌"
    echo "Revisa los mensajes anteriores y corrige los módulos indicados."
    exit 1
fi
