# -*- coding: utf-8 -*-
"""
main.py
----------------------------------
Punto de entrada del backend de Tutorín.
Ejecuta la aplicación creada en app.py.
✅ Integra slowapi para rate limiting global
"""

import os
import uvicorn
from app import app

# ✅ Integrar slowapi con la app
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# -------------------------------------------------------
# EJECUCIÓN
# -------------------------------------------------------
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=os.getenv("ENVIRONMENT", "development") == "development"
    )