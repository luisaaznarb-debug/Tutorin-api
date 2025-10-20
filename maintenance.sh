#!/bin/bash
# ==========================================================
# 🧰 Tutorín — Mantenimiento Completo del Sistema
# ----------------------------------------------------------
# Este script realiza:
#   1️⃣ Validación de todos los módulos y pistas
#   2️⃣ Generación automática de documentación
#   3️⃣ Copia de seguridad del núcleo del sistema
# ==========================================================

clear
echo "🧩=============================================================="
echo "🧠  TUTORÍN — MANTENIMIENTO AUTOMÁTICO DEL SISTEMA"
echo "🧩=============================================================="
echo ""

# ----------------------------------------------------------
# 1️⃣ Ejecutar pruebas automáticas
# ----------------------------------------------------------
if [ ! -f "./run_tests.sh" ]; then
    echo "⚠️  No se encontró run_tests.sh en el directorio actual."
    echo "   Asegúrate de ejecutarlo desde la raíz del proyecto."
    exit 1
fi

echo "🔍 Ejecutando pruebas completas..."
./run_tests.sh
tests_exit=$?

if [ $tests_exit -ne 0 ]; then
    echo "❌ Se detectaron errores durante las pruebas. Corrige antes de continuar."
    exit 1
fi

# ----------------------------------------------------------
# 2️⃣ Generar documentación con pdoc
# ----------------------------------------------------------
echo ""
echo "📘 Generando documentación automática..."
if ! command -v pdoc &> /dev/null
then
    echo "⚠️  pdoc no está instalado. Instalando automáticamente..."
    pip install pdoc -q
fi

DOCS_PATH="docs"
mkdir -p $DOCS_PATH
pdoc logic --html --output-dir $DOCS_PATH --force > /dev/null 2>&1

echo "✅ Documentación generada en: $DOCS_PATH/index.html"
echo ""

# ----------------------------------------------------------
# 3️⃣ Crear copia de seguridad del núcleo
# ----------------------------------------------------------
echo "💾 Creando copia de seguridad..."
DATE=$(date +"%Y-%m-%d_%H-%M")
BACKUP_DIR="backups/tutorin_backup_$DATE"

mkdir -p $BACKUP_DIR
mkdir -p backups

# Copiar las carpetas principales
cp -r logic/core $BACKUP_DIR/
cp -r modules $BACKUP_DIR/
cp -r tests $BACKUP_DIR/
cp run_tests.sh $BACKUP_DIR/ 2>/dev/null || true
cp maintenance.sh $BACKUP_DIR/ 2>/dev/null || true

echo "✅ Copia de seguridad creada en: $BACKUP_DIR"
echo ""

# ----------------------------------------------------------
# Final
# ----------------------------------------------------------
echo "🎉 MANTENIMIENTO COMPLETADO CON ÉXITO 🎉"
echo "---------------------------------------------"
echo "📊 Todas las pruebas superadas."
echo "📘 Documentación actualizada."
echo "💾 Copia de seguridad guardada."
echo ""
echo "🌈 Tutorín está listo para seguir creciendo sin errores 🚀"
