# -*- coding: utf-8 -*-
"""
routes/solve.py
Endpoint principal de Tutorín - CORREGIDO para usar hint_type real y contexto completo
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

class SolveRequest(BaseModel):
    user_id: Optional[str] = None
    question: str
    last_answer: Optional[str] = ""
    exercise_id: Optional[str] = None
    context: Optional[str] = ""
    cycle: Optional[str] = "c2"

def _canon(s: str) -> str:
    """Normaliza texto para comparación"""
    return str(s or "").replace(" ", "").replace(",", ".").lower()

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
    # 1️⃣ CASO "NO SÉ" → PISTA
    # ---------------------------------------------------
    if is_unknown_answer(req.last_answer or ""):
        error_count = min(9, error_count + 1)
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
    # 2️⃣ LLAMAR AL MOTOR
    # ---------------------------------------------------
    det = run_engine_for(
        engine,
        prompt=req.question,
        step=step_now,
        answer=req.last_answer or "",
        errors=error_count,
    )
    if not det:
        return {
            "exercise_id": exercise_id,
            "status": "error",
            "message": "No pude procesar este ejercicio.",
            "nlu": nlu,
        }
    
    message = det.get("message", "")
    expected = det.get("expected_answer")
    status = det.get("status", "ask")
    next_step = int(det.get("next_step", step_now))
    hint_type = det.get("hint_type", "general_error")

    # ---------------------------------------------------
    # 3️⃣ CASOS DE RESPUESTA
    # ---------------------------------------------------
    # 3a. Primera vez en este paso (sin respuesta todavía)
    if _canon(req.last_answer) == "":
        new_ctx = (prev_ctx + "\n" + message).strip()
        upsert_progress(exercise_id, step_now, error_count, new_ctx, user_id=req.user_id)
        save_history(
            req.user_id, exercise_id, req.question, req.last_answer, message, step_now, error_count
        )
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

    # 3b. HAY respuesta del usuario → verificar
    if not expected:
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
            "expected_answer": None,
            "context": new_ctx,
            "nlu": nlu,
        }

    # 3c. Respuesta INCORRECTA → incrementar errores, mantener paso
    if _canon(req.last_answer) != _canon(expected):
        error_count = min(9, error_count + 1)
        # 🔑 CAMBIO CLAVE: usa `message` como contexto, no `req.question`
        ai_hint = generate_hint_with_ai(
            topic,
            hint_type,
            message,  # ✅ CORREGIDO: contexto completo con HTML
            answer=req.last_answer or "",
            error_count=error_count,
            cycle=req.cycle,
        )
        feedback = f"❌ No es exactamente. {ai_hint if ai_hint else 'Revisa e intenta de nuevo.'}"
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

    # 3d. Respuesta CORRECTA → avanzar y mostrar siguiente paso
    if _canon(req.last_answer) == _canon(expected):
        success_msg = "✅ ¡Correcto! 👍"
        upsert_progress(exercise_id, next_step, 0, prev_ctx, user_id=req.user_id)
        save_history(
            req.user_id, exercise_id, req.question, req.last_answer, success_msg, next_step, 0
        )
        next_det = run_engine_for(
            engine,
            prompt=req.question,
            step=next_step,
            answer="",
            errors=0,
        )
        if next_det:
            next_message = next_det.get("message", "")
            next_expected = next_det.get("expected_answer")
            next_status = next_det.get("status", "ask")
            combined_message = f"{success_msg}\n\n{next_message}"
            new_ctx = (prev_ctx + "\n" + combined_message).strip()
            upsert_progress(exercise_id, next_step, 0, new_ctx, user_id=req.user_id)
            return {
                "exercise_id": exercise_id,
                "status": next_status,
                "step": next_step,
                "error_count": 0,
                "message": combined_message,
                "expected_answer": next_expected,
                "context": new_ctx,
                "nlu": nlu,
            }
        else:
            final_message = f"{success_msg}\n\n🎉 ¡Ejercicio completado!"
            new_ctx = (prev_ctx + "\n" + final_message).strip()
            upsert_progress(exercise_id, next_step, 0, new_ctx, user_id=req.user_id)
            return {
                "exercise_id": exercise_id,
                "status": "done",
                "step": next_step,
                "error_count": 0,
                "message": final_message,
                "expected_answer": None,
                "context": new_ctx,
                "nlu": nlu,
            }