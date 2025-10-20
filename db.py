# -*- coding: utf-8 -*-
import os
import sqlite3
from contextlib import contextmanager
from typing import Optional, Tuple, Dict, Any, List

DB_PATH = os.getenv("SQLITE_PATH", "tutorin.db")

def _init():
    with sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        cur.execute("""
CREATE TABLE IF NOT EXISTS progress (
    user_id TEXT,
    exercise_id TEXT PRIMARY KEY,
    step INTEGER NOT NULL DEFAULT 0,
    error_count INTEGER NOT NULL DEFAULT 0,
    context TEXT DEFAULT ""
);
""")
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

_init()

@contextmanager
def _conn():
    con = sqlite3.connect(DB_PATH)
    try:
        yield con
        con.commit()
    finally:
        con.close()

def get_progress(exercise_id: str) -> Tuple[int, int, str]:
    with _conn() as con:
        cur = con.cursor()
        cur.execute("SELECT step, error_count, context FROM progress WHERE exercise_id = ?", (exercise_id,))
        row = cur.fetchone()
        if not row:
            # Si no existe, crear con step=0 pero devolver sin reiniciar en el futuro
            cur.execute("INSERT INTO progress(exercise_id, step, error_count, context) VALUES (?,?,?,?)",
                (exercise_id, 0, 0, ""))
            con.commit()
            return 0, 0, ""
        else:
            step, err, ctx = int(row[0]), int(row[1]), row[2] or ""
            return step, err, ctx

        return int(row[0]), int(row[1]), row[2] or ""

def upsert_progress(exercise_id: str, step: int, error_count: int, context: str, user_id: Optional[str] = None) -> None:
    with _conn() as con:
        cur = con.cursor()
        cur.execute("SELECT exercise_id FROM progress WHERE exercise_id = ?", (exercise_id,))
        if cur.fetchone():
            cur.execute("UPDATE progress SET step=?, error_count=?, context=? WHERE exercise_id=?",
                        (step, error_count, context, exercise_id))
        else:
            cur.execute("INSERT INTO progress(exercise_id, step, error_count, context) VALUES (?,?,?,?)",
                        (exercise_id, step, error_count, context))

def save_history(user_id: Optional[str], exercise_id: str, question: str, last_answer: Optional[str], response: str, step: int, error_count: int) -> None:
    with _conn() as con:
        cur = con.cursor()
        cur.execute(
            "INSERT INTO history(user_id, exercise_id, question, last_answer, response, step, error_count) VALUES (?,?,?,?,?,?,?)",
            (user_id, exercise_id, question, last_answer, response, step, error_count)
        )

def list_history(user_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
    with _conn() as con:
        cur = con.cursor()
        if user_id:
            cur.execute("SELECT id, user_id, exercise_id, question, last_answer, response, step, error_count, created_at FROM history WHERE user_id=? ORDER BY id DESC LIMIT ?", (user_id, limit))
        else:
            cur.execute("SELECT id, user_id, exercise_id, question, last_answer, response, step, error_count, created_at FROM history ORDER BY id DESC LIMIT ?", (limit,))
        cols = [c[0] for c in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]
