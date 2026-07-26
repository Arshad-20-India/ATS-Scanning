"""
CachedEmbedder: a decorator over any IEmbedder that caches computed
vectors in ICache, keyed by a hash of the text.

The concrete motivation: MatchingPolicy re-embeds JD requirement text
and resume bullets on every analysis. The same JD is commonly matched
against many resumes, and the same boilerplate resume bullets ("Led a
team of...", "Built a REST API...") recur across many different
resumes. Caching by text hash means the (comparatively expensive)
embedding model call only happens once per distinct string, not once
per analysis.
"""

from __future__ import annotations

import hashlib
import json
from typing import List, Optional

from app.core.config import settings
from app.domain.ports.cache import ICache
from app.domain.ports.embedder import IEmbedder


class CachedEmbedder(IEmbedder):
    def __init__(
        self,
        inner: IEmbedder,
        cache: ICache,
        cache_key_prefix: str = "embedding",
        ttl_seconds: Optional[int] = None,
    ) -> None:
        self._inner = inner
        self._cache = cache
        self._prefix = cache_key_prefix
        self._ttl = (
            ttl_seconds if ttl_seconds is not None else settings.embedding_cache_ttl_seconds
        )

    def embed(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []

        results: List[Optional[List[float]]] = [None] * len(texts)
        uncached_indices: List[int] = []
        uncached_texts: List[str] = []

        for i, text in enumerate(texts):
            cached = self._cache.get(self._key_for(text))
            if cached is not None:
                results[i] = json.loads(cached)
            else:
                uncached_indices.append(i)
                uncached_texts.append(text)

        if uncached_texts:
            fresh_vectors = self._inner.embed(uncached_texts)
            for idx, text, vector in zip(uncached_indices, uncached_texts, fresh_vectors):
                results[idx] = vector
                self._cache.set(self._key_for(text), json.dumps(vector), ttl_seconds=self._ttl)

        return results  # type: ignore[return-value]  -- every slot filled by this point

    def similarity(self, vector_a: List[float], vector_b: List[float]) -> float:
        # Similarity is a cheap local computation (no model call), so
        # it's delegated directly rather than cached.
        return self._inner.similarity(vector_a, vector_b)

    def _key_for(self, text: str) -> str:
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        return f"{self._prefix}:{digest}"
