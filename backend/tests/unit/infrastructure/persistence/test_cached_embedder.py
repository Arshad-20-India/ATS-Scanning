from __future__ import annotations

from typing import List

from app.domain.ports.embedder import IEmbedder
from app.infrastructure.nlp.cached_embedder import CachedEmbedder
from app.infrastructure.persistence.redis_cache import RedisCache


class CountingEmbedder(IEmbedder):
    """Tracks how many times the underlying model was actually called."""

    def __init__(self) -> None:
        self.embed_call_count = 0
        self.texts_seen: List[str] = []

    def embed(self, texts: List[str]) -> List[List[float]]:
        self.embed_call_count += 1
        self.texts_seen.extend(texts)
        return [[float(len(t)), 0.0] for t in texts]

    def similarity(self, vector_a, vector_b) -> float:
        return 1.0 if vector_a == vector_b else 0.0


def test_first_call_hits_inner_embedder(redis_client):
    inner = CountingEmbedder()
    cache = RedisCache(client=redis_client)
    cached = CachedEmbedder(inner, cache)

    result = cached.embed(["hello world"])

    assert result == [[11.0, 0.0]]
    assert inner.embed_call_count == 1


def test_second_call_with_same_text_uses_cache_not_inner_embedder(redis_client):
    inner = CountingEmbedder()
    cache = RedisCache(client=redis_client)
    cached = CachedEmbedder(inner, cache)

    cached.embed(["hello world"])
    result = cached.embed(["hello world"])

    assert result == [[11.0, 0.0]]
    assert inner.embed_call_count == 1  # NOT called a second time


def test_mixed_cached_and_uncached_texts_only_computes_uncached(redis_client):
    inner = CountingEmbedder()
    cache = RedisCache(client=redis_client)
    cached = CachedEmbedder(inner, cache)

    cached.embed(["cached text"])  # warms the cache
    result = cached.embed(["cached text", "new text"])

    assert result == [[11.0, 0.0], [8.0, 0.0]]
    assert inner.embed_call_count == 2  # 1st call + 1 more for only "new text"
    assert inner.texts_seen == ["cached text", "new text"]  # "cached text" not re-sent


def test_empty_list_short_circuits_without_touching_cache_or_inner(redis_client):
    inner = CountingEmbedder()
    cache = RedisCache(client=redis_client)
    cached = CachedEmbedder(inner, cache)

    assert cached.embed([]) == []
    assert inner.embed_call_count == 0


def test_similarity_delegates_to_inner_without_caching(redis_client):
    inner = CountingEmbedder()
    cache = RedisCache(client=redis_client)
    cached = CachedEmbedder(inner, cache)

    result = cached.similarity([1.0, 2.0], [1.0, 2.0])
    assert result == 1.0


def test_different_texts_produce_different_cache_entries(redis_client):
    inner = CountingEmbedder()
    cache = RedisCache(client=redis_client)
    cached = CachedEmbedder(inner, cache)

    cached.embed(["text a", "text b"])
    assert inner.embed_call_count == 1

    # Same two texts again -> both cache hits, no new inner call.
    cached.embed(["text a", "text b"])
    assert inner.embed_call_count == 1
