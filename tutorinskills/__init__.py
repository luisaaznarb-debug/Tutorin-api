from typing import Callable, Dict, List, Optional
from pydantic import BaseModel

# ============
# Modelo de paso
# ============
class Step(BaseModel):
    text: str
    imageUrl: Optional[str] = None

# ============
# Motor de resolución
# ============
engine: Dict[str, Callable[[str], List[Step]]] = {}

# ============
# Funciones de habilidades (skills)
# ============

# 🧮 Matemáticas
def add_fractions(user_input: str) -> List[Step]:
    return [
        Step(text="Paso 1: Busca el mínimo común múltiplo (MCM) de los denominadores."),
        Step(text="Paso 2: Convierte ambas fracciones al mismo denominador."),
        Step(text="Paso 3: Suma los numeradores."),
        Step(
            text="Paso 4: Simplifica la fracción final si es posible.",
            imageUrl="https://upload.wikimedia.org/wikipedia/commons/thumb/3/35/Simplify_fraction.svg/300px-Simplify_fraction.svg.png"
        ),
    ]

def simple_sum(user_input: str) -> List[Step]:
    return [
        Step(text="Paso 1: Identifica los números que se deben sumar."),
        Step(text="Paso 2: Suma en columna si son números grandes."),
        Step(text="Paso 3: Verifica tu resultado."),
    ]

# 📚 Lengua
def grammar_nouns(user_input: str) -> List[Step]:
    return [
        Step(text="Paso 1: Identifica el sustantivo en la frase.", imageUrl="https://api.arasaac.org/api/pictograms/4647"),
        Step(text="Paso 2: Pregúntate si es una persona, animal, cosa o lugar."),
        Step(text="Paso 3: Decide si es un sustantivo común o propio."),
    ]

def verb_tenses(user_input: str) -> List[Step]:
    return [
        Step(text="Paso 1: Encuentra el verbo en la oración.", imageUrl="https://api.arasaac.org/api/pictograms/5230"),
        Step(text="Paso 2: Piensa si la acción ocurre en el pasado, presente o futuro."),
        Step(text="Paso 3: Intenta conjugar el verbo en otro tiempo."),
    ]

# 🌍 Historia y geografía
def history_kings(user_input: str) -> List[Step]:
    return [
        Step(text="Paso 1: ¿De qué época histórica estamos hablando?", imageUrl="https://api.arasaac.org/api/pictograms/21771"),
        Step(text="Paso 2: ¿Qué reyes o personajes importantes aparecen?"),
        Step(text="Paso 3: ¿Qué hicieron? ¿Por qué fueron importantes?"),
    ]

def map_reading(user_input: str) -> List[Step]:
    return [
        Step(text="Paso 1: Observa la rosa de los vientos en el mapa.", imageUrl="https://api.arasaac.org/api/pictograms/26504"),
        Step(text="Paso 2: Identifica los puntos cardinales: norte, sur, este, oeste."),
        Step(text="Paso 3: Localiza dónde ocurre la acción en el mapa."),
    ]

# 🔬 Ciencias
def parts_of_plant(user_input: str) -> List[Step]:
    return [
        Step(text="Paso 1: Identifica las partes de la planta (raíz, tallo, hojas, flor).", imageUrl="https://api.arasaac.org/api/pictograms/1809"),
        Step(text="Paso 2: Describe qué función tiene cada parte."),
        Step(text="Paso 3: Dibuja o nombra una planta que conozcas."),
    ]

def water_cycle(user_input: str) -> List[Step]:
    return [
        Step(text="Paso 1: El sol calienta el agua de ríos y mares.", imageUrl="https://api.arasaac.org/api/pictograms/15676"),
        Step(text="Paso 2: El agua se evapora y sube como vapor."),
        Step(text="Paso 3: Se condensa formando nubes.", imageUrl="https://api.arasaac.org/api/pictograms/50311"),
        Step(text="Paso 4: Luego llueve y el agua vuelve a la tierra."),
    ]

# ============
# Registro de habilidades
# ============
engine["frac:add"] = add_fractions
engine["math:add"] = simple_sum
engine["grammar:nouns"] = grammar_nouns
engine["grammar:verbs"] = verb_tenses
engine["history:kings"] = history_kings
engine["geo:map"] = map_reading
engine["science:plant"] = parts_of_plant
engine["science:water"] = water_cycle

# ============
# Detección automática de skill
# ============
def detectSkill(user_input: str) -> Optional[str]:
    s = user_input.lower()

    if any(op in s for op in ["fracción", "/", "octavos", "tercios", "sumar fracciones"]):
        return "frac:add"
    if any(op in s for op in ["sumar", "más", "+", "cuánto es", "suma"]):
        return "math:add"
    if any(op in s for op in ["sustantivo", "nombre", "persona, animal, cosa"]):
        return "grammar:nouns"
    if any(op in s for op in ["verbo", "tiempo verbal", "conjugar"]):
        return "grammar:verbs"
    if any(op in s for op in ["rey", "época", "personaje histórico", "reinado"]):
        return "history:kings"
    if any(op in s for op in ["mapa", "rosa de los vientos", "puntos cardinales", "norte"]):
        return "geo:map"
    if any(op in s for op in ["planta", "hojas", "raíces", "tallo", "flor"]):
        return "science:plant"
    if any(op in s for op in ["ciclo del agua", "evaporación", "condensación", "lluvia"]):
        return "science:water"

    return None
