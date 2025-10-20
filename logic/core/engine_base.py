# -*- coding: utf-8 -*-
"""
engine_base.py
--------------------------------------------------
Clase base para todos los motores educativos de Tutorín.

✔️ Estandariza estructura y formato de salida.
✔️ Valida automáticamente los resultados.
✔️ Facilita la extensión a nuevas materias.
"""

from typing import Any, Dict
from .engine_schema import validate_output


class BaseEngine:
    """
    Clase base que define la interfaz común para todos los motores.
    Cada motor que herede de esta clase deberá implementar el método
    `handle_step(prompt, step, answer, errors)`.
    """

    # Metadatos comunes
    topic: str = "general"        # Ej: "matematica", "lengua", ...
    hint_prefix: str = "general"  # Ej: "add_col", "decimal_alinear", ...
    name: str = "base_engine"     # Nombre interno (útil para logs y depuración)

    # ---------------------------------------------------
    # MÉTODO PRINCIPAL QUE DEBEN HEREDAR LOS MOTORES
    # ---------------------------------------------------
    def handle_step(self, prompt: str, step: int, answer: str, errors: int) -> Dict[str, Any]:
        """
        Debe ser implementado por cada motor.
        Retorna un dict compatible con ENGINE_OUTPUT_SCHEMA.
        """
        raise NotImplementedError("El motor debe implementar handle_step()")

    # ---------------------------------------------------
    # ENVOLTORIO DE EJECUCIÓN CON VALIDACIÓN
    # ---------------------------------------------------
    def run(self, prompt: str, step: int, answer: str, errors: int) -> Dict[str, Any]:
        """
        Ejecuta el motor, valida su salida y devuelve el resultado.
        """
        try:
            output = self.handle_step(prompt, step, answer, errors)
            if not validate_output(output, self.name):
                print(f"[ENGINE_BASE] ⚠️ Motor {self.name} devolvió formato no válido.")
            return output
        except Exception as e:
            print(f"[ENGINE_BASE] ❌ Error en {self.name}: {e}")
            return {
                "status": "error",
                "message": f"Se produjo un error en el motor {self.name}: {str(e)}",
                "expected_answer": None,
                "topic": self.topic,
                "hint_type": f"{self.hint_prefix}_error",
                "next_step": step
            }

    # ---------------------------------------------------
    # UTILIDAD: METADATOS
    # ---------------------------------------------------
    def info(self) -> Dict[str, str]:
        """
        Devuelve información descriptiva del motor.
        """
        return {
            "name": self.name,
            "topic": self.topic,
            "hint_prefix": self.hint_prefix,
            "doc": (self.__doc__ or "").strip()
        }
