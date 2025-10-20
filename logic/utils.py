# -*- coding: utf-8 -*-
import re

def is_unknown_answer(text: str) -> bool:
    if not text:
        return False
    t = text.strip().lower()
    return t in {"no se", "nose", "no lo se", "no lo sé", "ni idea", "no sé", "no entiendo"} or bool(re.search(r"no.*(se|sé)", t))
