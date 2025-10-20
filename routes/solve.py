# -*- coding: utf-8 -*-
"""
routes/solve.py
Endpoint principal de Tutorín.
Totalmente sincronizado con tus motores:
- No añade ni modifica mensajes.
- Solo gestiona flujo, persistencia y errores.
"""

from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel
import uuid

from modules.ai_analyzer import analyze_prompt, run_engine_for
from logic.utils import is_unknown_answer
from logic.ai_hints.ai_router import generate_hint_with_ai
from db import get_progress, upsert_progress, save_history

router = APIRouter()

# -------------------------------------------------------
# MODELO DE PETICIÓN
# -------------------------------------------------------
class SolveRequest(BaseModel):
    user_id: Optional[str] = None
    question: str
    last_answer: Optional[str] = ""
    exercise_id: Optional[str] = None
    context: Optional[str] = ""
    cycle: Optional[str] = "c2"  # c1, c2, c3

# -------------------------------------------------------
# HELPERS
# -------------------------------------------------------
def _canon(s: str) -> str:
    return str(s or "").replace(" ", "").replace(",", ".").lower()

# -------------------------------------------------------
# ENDPOINT PRINCIPAL
# -------------------------------------------------------
@router.post("/")
def solve(req: SolveRequest):
    """Orquestador principal: gestiona paso actual, errores y motores."""
    exercise_id = req.exercise_id or str(uuid.uuid4())

    # Leer progreso actual
    step_now, error_count, prev_ctx = get_progress(exercise_id)

    # Detectar tema y motor
    nlu = analyze_prompt(req.question or "")
    engine = nlu.get("engine") or "generic_engine"
    topic = nlu.get("intent") or "general"

    # ---------------------------------------------------
    # 1️⃣ CASO "NO SÉ" → PISTA (internas o IA)
    # ---------------------------------------------------
    if is_unknown_answer(req.last_answer or ""):
        ai_hint = generate_hint_with_ai(
            topic,
            f"hint_{step_now}",
            req.question,
            answer=req.last_answer or "",
            error_count=error_count,
            cycle=req.cycle,
        )
        msg = ai_hint or "🧠 Pista: piensa paso a paso y revisa los números."
        new_ctx = (prev_ctx + "\n" + msg).strip()
        upsert_progress(exercise_id, step_now, error_count, new_ctx, user_id=req.user_id)
        save_history(
            req.user_id, exercise_id, req.question, req.last_answer, msg, step_now, error_count
        )
        return {
            "exercise_id": exercise_id,
            "status": "hint",
            "step": step_now,
            "error_count": error_count,
            "message": msg,
            "expected_answer": None,
            "context": new_ctx,
            "nlu": nlu,
        }

    # ---------------------------------------------------
    # 2️⃣ LLAMAR AL MOTOR CORRESPONDIENTE
    # ---------------------------------------------------
    det = run_engine_for(
        engine,
        prompt=req.question,
        step=step_now,
        answer=req.last_answer or "",
        errors=error_count,
    )

    # Los motores definen todo: message, status, expected_answer, next_step
    message = det.get("message", "")
    expected = det.get("expected_answer")
    status = det.get("status", "ask")
    next_step = int(det.get("next_step", step_now))
    step_tag = det.get("step_tag", "")

    # Guardar historial
    save_history(
        req.user_id, exercise_id, req.question, req.last_answer, message, step_now, error_count
    )

    # ---------------------------------------------------
    # 3️⃣ RESPUESTAS
    # ---------------------------------------------------

    # 3a. Primera vez de este paso (no hay respuesta todavía)
    if expected and _canon(req.last_answer) == "":
        new_ctx = (prev_ctx + "\n" + message).strip()
        upsert_progress(exercise_id, step_now, error_count, new_ctx, user_id=req.user_id)
        return {
            "exercise_id": exercise_id,
            "status": status,
            "step": step_now,
            "error_count": error_count,
            "message": message,
            "expected_answer": expected,
            "context": new_ctx,
            "nlu": nlu,
        }

    # 3b. Respuesta incorrecta → se mantiene el paso
    if expected and _canon(req.last_answer) != _canon(expected):
        error_count = min(9, (error_count or 0) + 1)
        feedback = f"❌ No es exactamente.\n{message}"
        new_ctx = (prev_ctx + "\n" + feedback).strip()
        upsert_progress(exercise_id, step_now, error_count, new_ctx, user_id=req.user_id)
        save_history(
            req.user_id, exercise_id, req.question, req.last_answer, feedback, step_now, error_count
        )
        return {
            "exercise_id": exercise_id,
            "status": "feedback",
            "step": step_now,
            "error_count": error_count,
            "message": feedback,
            "expected_answer": expected,
            "context": new_ctx,
            "nlu": nlu,
        }

    # 3c. Respuesta correcta → avanzar al siguiente paso
    if expected and _canon(req.last_answer) == _canon(expected):
        new_ctx = (prev_ctx + "\n" + message).strip()
        upsert_progress(exercise_id, next_step, 0, new_ctx, user_id=req.user_id)
        save_history(
            req.user_id, exercise_id, req.question, req.last_answer, message, next_step, 0
        )
        return {
            "exercise_id": exercise_id,
            "status": status,
            "step": next_step,
            "error_count": 0,
            "message": message,
            "expected_answer": expected,
            "context": new_ctx,
            "nlu": nlu,
        }

    # 3d. Caso general sin expected (mensaje libre del motor)
    new_ctx = (prev_ctx + "\n" + message).strip()
    upsert_progress(exercise_id, step_now, error_count, new_ctx, user_id=req.user_id)
    return {
        "exercise_id": exercise_id,
        "status": status,
        "step": step_now,
        "error_count": error_count,
        "message": message,
        "context": new_ctx,
        "nlu": nlu,
    }
