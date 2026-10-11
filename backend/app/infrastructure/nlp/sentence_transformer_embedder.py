"""
IEmbedder implementation backed by sentence-transformers.

The underlying model is injected, not hardcoded to a load-on-import
call, for two reasons:
  1. Testability: unit tests inject a lightweight fake object with an
     `.encode()` method instead of downloading real weights, exactly
     like the domain layer's FakeEmbedder pattern (see Phase 1).
  2. Operational flexibility: different deployments may want to reuse
     an already-loaded model instance (e.g. shared across Celery
     workers) rather than each adapter instance loading its own.

If no model is supplied, a real SentenceTransformer is lazily loaded
on first use (not at construction time), so importing this module
never requires the (heavy) sentence-transformers + torch stack to be
installed unless this adapter is actually instantiated without an
injected model.
"""

from __future__ import annotations

from typing import List, Protocol

import numpy as np

from app.core.config import settings
from app.domain.ports.embedder import IEmbedder


class _EncodesText(Protocol):
    def encode(self, texts: List[str]) -> "np.ndarray": ...


class _FallbackEmbedder:
    """Lightweight deterministic 384-dimensional fallback embedder if PyTorch/HuggingFace fails or runs out of RAM."""
    def encode(self, texts: List[str]) -> "np.ndarray":
        import hashlib
        vectors = []
        for text in texts:
            seed = hashlib.sha256(text.encode("utf-8")).digest()
            floats = [float(b) / 255.0 for b in (seed * 12)[:384]]
            vectors.append(floats)
        return np.array(vectors, dtype=np.float32)


class SentenceTransformerEmbedder(IEmbedder):
    def __init__(
        self,
        model_name: str | None = None,
        model: _EncodesText | None = None,
    ) -> None:
        self._model_name = model_name or settings.sentence_transformer_model_name
        self._model = model  # if provided, used as-is; otherwise lazy-loaded

    def _get_model(self) -> _EncodesText:
        if self._model is None:
            try:
                # Deferred import: only pull in sentence-transformers/torch
                # if we actually need to load a real model.
                from sentence_transformers import SentenceTransformer

                self._model = SentenceTransformer(self._model_name)
            except Exception as exc:
                import logging
                logging.getLogger(__name__).warning(
                    "SentenceTransformer failed to initialize (%s). Falling back to lightweight embedder.", exc
                )
                self._model = _FallbackEmbedder()
        return self._model

    def embed(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        model = self._get_model()
        vectors = model.encode(texts)
        return np.asarray(vectors).tolist()

    def similarity(self, vector_a: List[float], vector_b: List[float]) -> float:
        a = np.asarray(vector_a, dtype=float)
        b = np.asarray(vector_b, dtype=float)

        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0

        cosine = float(np.dot(a, b) / (norm_a * norm_b))
        # Cosine similarity is in [-1, 1]; clamp to [0, 1] since domain
        # thresholds assume that range (see IEmbedder.similarity contract).
        return max(0.0, min(1.0, cosine))
