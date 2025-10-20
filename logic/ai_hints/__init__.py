# Paquete de pistas (AI hints) de Tutorin.
# Incluye módulos especializados por tipo de operación.
# Cada módulo contiene funciones progresivas (nivel C2) con refuerzos y soluciones automáticas.

from .hints_utils import *
from .hints_addition import _sum_col_hint
from .hints_subtraction import _sub_col_hint
from .hints_multiplication import _mult_parcial_hint
from .hints_division import _division_hint
from .hints_fractions import (
    _frac_mcm_hint,
    _frac_equiv_hint,
    _frac_operacion_hint,
    _frac_simplificar_hint,
)
from .ai_router import generate_hint_with_ai

__all__ = [
    "_sum_col_hint",
    "_sub_col_hint",
    "_mult_parcial_hint",
    "_division_hint",
    "_frac_mcm_hint",
    "_frac_equiv_hint",
    "_frac_operacion_hint",
    "_frac_simplificar_hint",
    "generate_hint_with_ai",
]
