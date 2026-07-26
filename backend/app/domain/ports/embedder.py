from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List


class IEmbedder(ABC):
    """
    Port for turning text into vectors and comparing them.

    Implemented in infrastructure by a Sentence-Transformers adapter.
    The domain layer never imports sentence-transformers directly —
    only this interface — so the embedding backend can be swapped
    (different model, different library, remote embedding API) without
    touching any scoring logic, and tests can use a trivial fake
    embedder instead of loading a real model.
    """

    @abstractmethod
    def embed(self, texts: List[str]) -> List[List[float]]:
        """Return one embedding vector per input text, same order."""
        raise NotImplementedError

    @abstractmethod
    def similarity(self, vector_a: List[float], vector_b: List[float]) -> float:
        """
        Return a similarity score in [0, 1] (typically cosine similarity
        rescaled/clamped). Implementations must guarantee the output
        range so domain thresholds remain meaningful regardless of
        backend.
        """
        raise NotImplementedError
