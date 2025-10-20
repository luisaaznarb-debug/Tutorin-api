# -*- coding: utf-8 -*-
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class SolveRequest(BaseModel):
    user_id: Optional[str] = Field(default=None, description="Identificador del alumno (opcional en local)")
    question: str
    last_answer: Optional[str] = ""
    exercise_id: Optional[str] = None
    context: Optional[str] = ""
    cycle: Optional[str] = "c2"  # c1, c2, c3

class SolveResponse(BaseModel):
    exercise_id: str
    status: str
    step: int
    error_count: int
    message: str
    expected_answer: Optional[str] = None
    context: Optional[str] = None
    nlu: Optional[Dict[str, Any]] = None

class HistoryItem(BaseModel):
    id: int
    user_id: Optional[str]
    exercise_id: str
    question: str
    last_answer: Optional[str]
    response: str
    step: int
    error_count: int
    created_at: str
