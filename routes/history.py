# -*- coding: utf-8 -*-
from fastapi import APIRouter, Query
from typing import Optional
from db import list_history

router = APIRouter()

@router.get("/")
def get_history(user_id: Optional[str] = Query(default=None), limit: int = Query(default=50, ge=1, le=200)):
    return {"items": list_history(user_id=user_id, limit=limit)}
