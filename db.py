# -*- coding: utf-8 -*-
"""
db.py
----------------------------------
Gestión de base de datos para Tutorín (SQLite)
"""

import os
import sqlite3
import logging
from contextlib import contextmanager
from typing import Optional, Tuple, Dict, Any, List

logger = logging.getLogger("tutorin.db")

# Ruta de la base de datos SQLite
DB_PATH = os.getenv("SQLITE_PATH", "tutorin.db")

# -------------------------------------------------------
# CONEXIÓN
# -------------------------------------------------------
@contextmanager
def _conn():
    """Context manager para SQLite"""
    con = sqlite3.connect(DB_PATH)
    try:
        yield con
        con.commit()
    except Exception as e:
        con.rollback()
        logger.error(f"❌ Error en transacción DB: {e}")
        raise
    finally:
        con.close()

# -------------------------------------------------------
# INICIALIZACIÓN DE TABLAS
# -------------------------------------------------------
def _init():
    """Crea las tablas si no existen"""
    with _conn() as con:
        cur = con.cursor()
        
        # Tabla de progreso
        cur.execute("""
            CREATE TABLE IF NOT EXISTS progress (
                user_id TEXT,
                exercise_id TEXT PRIMARY KEY,
                step INTEGER NOT NULL DEFAULT 0,
                error_count INTEGER NOT NULL DEFAULT 0,
                context TEXT DEFAULT ""
            );
        """)
        
        # Tabla de historial
        cur.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                exercise_id TEXT,
                question TEXT,
                last_answer TEXT,
                response TEXT,
                step INTEGER,
                error_count INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        con.commit()
        logger.info("✅ Tablas SQLite inicializadas correctamente")

# Inicializar al importar
try:
    _init()
    logger.info(f"📁 Base de datos SQLite: {DB_PATH}")
except Exception as e:
    logger.error(f"❌ Error inicializando DB: {e}")

# -------------------------------------------------------
# FUNCIONES DE ACCESO
# -------------------------------------------------------

def get_progress(exercise_id: str) -> Tuple[int, int, str]:
    """Obtiene el progreso de un ejercicio"""
    with _conn() as con:
        cur = con.cursor()
        cur.execute(
            "SELECT step, error_count, context FROM progress WHERE exercise_id = ?",
            (exercise_id,)
        )
        row = cur.fetchone()
        
        if not row:
            # Si no existe, crear con step=0
            cur.execute(
                "INSERT INTO progress(exercise_id, step, error_count, context) VALUES (?,?,?,?)",
                (exercise_id, 0, 0, "")
            )
            con.commit()
            return 0, 0, ""
        else:
            step, err, ctx = int(row[0]), int(row[1]), row[2] or ""
            return step, err, ctx


def upsert_progress(exercise_id: str, step: int, error_count: int, context: str, user_id: Optional[str] = None) -> None:
    """Actualiza o inserta el progreso de un ejercicio"""
    with _conn() as con:
        cur = con.cursor()
        
        # Verificar si existe
        cur.execute("SELECT exercise_id FROM progress WHERE exercise_id = ?", (exercise_id,))
        
        if cur.fetchone():
            # UPDATE
            cur.execute(
                "UPDATE progress SET step=?, error_count=?, context=?, user_id=? WHERE exercise_id=?",
                (step, error_count, context, user_id, exercise_id)
            )
        else:
            # INSERT
            cur.execute(
                "INSERT INTO progress(exercise_id, step, error_count, context, user_id) VALUES (?,?,?,?,?)",
                (exercise_id, step, error_count, context, user_id)
            )


def save_history(user_id: Optional[str], exercise_id: str, question: str, last_answer: Optional[str], response: str, step: int, error_count: int) -> None:
    """Guarda un evento en el historial"""
    with _conn() as con:
        cur = con.cursor()
        cur.execute(
            "INSERT INTO history(user_id, exercise_id, question, last_answer, response, step, error_count) VALUES (?,?,?,?,?,?,?)",
            (user_id, exercise_id, question, last_answer, response, step, error_count)
        )


def list_history(user_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
    """Lista el historial de interacciones"""
    with _conn() as con:
        cur = con.cursor()
        
        if user_id:
            cur.execute(
                "SELECT id, user_id, exercise_id, question, last_answer, response, step, error_count, created_at FROM history WHERE user_id=? ORDER BY id DESC LIMIT ?",
                (user_id, limit)
            )
        else:
            cur.execute(
                "SELECT id, user_id, exercise_id, question, last_answer, response, step, error_count, created_at FROM history ORDER BY id DESC LIMIT ?",
                (limit,)
            )
        
        cols = [c[0] for c in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


def reset_progress(exercise_id: str) -> None:
    """Resetea el progreso de un ejercicio"""
    with _conn() as con:
        cur = con.cursor()
        cur.execute("DELETE FROM progress WHERE exercise_id = ?", (exercise_id,))
        logger.info(f"🔄 Progreso reseteado para ejercicio: {exercise_id}")


def reset_all() -> None:
    """Borra TODA la base de datos (usar con cuidado)"""
    with _conn() as con:
        cur = con.cursor()
        cur.execute("DELETE FROM progress")
        cur.execute("DELETE FROM history")
        logger.warning("⚠️ Base de datos completamente reseteada")