"""
Singleton spaCy pipeline loader.

Loading a spaCy model takes real time (tens to hundreds of ms) and
holds real memory, so it must be loaded once per process, not once per
request. `lru_cache` gives us a trivial thread-safe-enough singleton
without introducing a DI framework at this layer.
"""

from __future__ import annotations

from functools import lru_cache

import spacy
from spacy.language import Language

from app.core.config import settings


@lru_cache(maxsize=1)
def get_nlp() -> Language:
    return spacy.load(settings.spacy_model_name)
