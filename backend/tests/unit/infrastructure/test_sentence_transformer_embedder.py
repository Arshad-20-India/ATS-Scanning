from __future__ import annotations

import numpy as np
import pytest

from app.infrastructure.nlp.sentence_transformer_embedder import (
    SentenceTransformerEmbedder,
)


class _FakeModel:
    """Stands in for a real SentenceTransformer: deterministic, no I/O."""

    def encode(self, texts):
        # Map each text to a fixed vector based on its length, purely
        # so we get deterministic, distinguishable vectors for testing.
        return np.array([[float(len(t)), float(t.count(" "))] for t in texts])


def test_embed_returns_one_vector_per_text():
    embedder = SentenceTransformerEmbedder(model=_FakeModel())
    vectors = embedder.embed(["hello world", "a"])
    assert len(vectors) == 2
    assert len(vectors[0]) == 2


def test_embed_empty_list_returns_empty_list():
    embedder = SentenceTransformerEmbedder(model=_FakeModel())
    assert embedder.embed([]) == []


def test_similarity_identical_vectors_is_one():
    embedder = SentenceTransformerEmbedder(model=_FakeModel())
    assert embedder.similarity([1.0, 2.0, 3.0], [1.0, 2.0, 3.0]) == pytest.approx(1.0)


def test_similarity_orthogonal_vectors_is_zero():
    embedder = SentenceTransformerEmbedder(model=_FakeModel())
    assert embedder.similarity([1.0, 0.0], [0.0, 1.0]) == pytest.approx(0.0)


def test_similarity_clamped_to_zero_one_range():
    embedder = SentenceTransformerEmbedder(model=_FakeModel())
    # Opposite vectors would give cosine = -1 without clamping.
    result = embedder.similarity([1.0, 0.0], [-1.0, 0.0])
    assert 0.0 <= result <= 1.0
    assert result == 0.0


def test_similarity_zero_vector_returns_zero():
    embedder = SentenceTransformerEmbedder(model=_FakeModel())
    assert embedder.similarity([0.0, 0.0], [1.0, 1.0]) == 0.0


def test_injected_model_is_used_without_loading_real_library():
    # If this test can run at all without sentence-transformers/torch
    # installed, it proves the lazy-import design works correctly.
    embedder = SentenceTransformerEmbedder(model=_FakeModel())
    vectors = embedder.embed(["test"])
    assert vectors == [[4.0, 0.0]]
