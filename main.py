# -*- coding: utf-8 -*-
"""
main.py
----------------------------------
Punto de entrada del backend de Tutorín.
Ejecuta la aplicación creada en app.py.
"""

import uvicorn
from app import app

# -------------------------------------------------------
# EJECUCIÓN
# -------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
