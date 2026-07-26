"""
Launches the real API app, wired with a fast deterministic embedder
instead of the real Sentence-Transformers model, specifically for
reproducible local benchmarking.

Why not benchmark with the real embedder: this sandbox can't reach
huggingface.co (see backend/README.md's Phase 2 notes), so a real
SentenceTransformerEmbedder would fail on first use here regardless.
More importantly, benchmarking the *embedding model's* inference time
would be measuring PyTorch/the model, not this codebase -- the
meaningful thing to measure and report honestly is the platform's own
pipeline: file parsing, section extraction, deterministic scoring, and
the full HTTP/DB round trip. This script isolates exactly that.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import List

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

import uvicorn

from app.api.main import create_app
from app.application.container import build_container
from app.domain.ports.embedder import IEmbedder


class FastDeterministicEmbedder(IEmbedder):
    """
    Zero-model-load, zero-network embedder: hashes text into a small
    fixed-size vector. Not semantically meaningful (this is a
    benchmark tool, not a correctness test), but deterministic and
    fast, so it isolates the platform's own pipeline latency from any
    ML model's inference time.
    """

    def embed(self, texts: List[str]) -> List[List[float]]:
        import hashlib

        vectors = []
        for text in texts:
            digest = hashlib.sha256(text.encode("utf-8")).digest()
            vectors.append([b / 255.0 for b in digest[:16]])
        return vectors

    def similarity(self, vector_a: List[float], vector_b: List[float]) -> float:
        dot = sum(a * b for a, b in zip(vector_a, vector_b))
        norm_a = sum(a * a for a in vector_a) ** 0.5
        norm_b = sum(b * b for b in vector_b) ** 0.5
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return max(0.0, min(1.0, dot / (norm_a * norm_b)))


if __name__ == "__main__":
    container = build_container(embedder=FastDeterministicEmbedder(), use_llm=False)
    app = create_app(container=container)
    uvicorn.run(app, host="127.0.0.1", port=8010, log_level="warning")
