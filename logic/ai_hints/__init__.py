# -*- coding: utf-8 -*-
"""
Paquete de pistas (AI hints) de Tutorín.
Sistema modular mejorado con funciones get_hint() públicas.
"""

# Importar funciones públicas de cada módulo
from .hints_addition import get_hint as get_addition_hint
from .hints_subtraction import get_hint as get_subtraction_hint
from .hints_multiplication import get_hint as get_multiplication_hint
from .hints_division import get_hint as get_division_hint
from .hints_fractions import get_hint as get_fractions_hint
from .hints_decimals import get_hint as get_decimals_hint
from .hints_geometry import get_hint as get_geometry_hint
from .hints_measures import get_hint as get_measures_hint
from .hints_percentages import get_hint as get_percentages_hint
from .hints_statistics import get_hint as get_statistics_hint
from .hints_problems import get_hint as get_problems_hint

# Importar el router principal
from .ai_router import generate_hint_with_ai

# Exportar todas las funciones públicas
__all__ = [
    "get_addition_hint",
    "get_subtraction_hint",
    "get_multiplication_hint",
    "get_division_hint",
    "get_fractions_hint",
    "get_decimals_hint",
    "get_geometry_hint",
    "get_measures_hint",
    "get_percentages_hint",
    "get_statistics_hint",
    "get_problems_hint",
    "generate_hint_with_ai",
]