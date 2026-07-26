"""
ICache implementation backed by Redis.

Same injectable-client pattern used throughout the infrastructure
layer: tests can supply a real redis.Redis client pointed at a real
(local, ephemeral) Redis instance -- unlike Sentence-Transformers/
OpenAI, Redis has no external network dependency, so this is tested
against the genuine adapter, not a fake.
"""

from __future__ import annotations

from typing import Optional

import redis

from app.core.config import settings
from app.domain.ports.cache import ICache


class RedisCache(ICache):
    def __init__(
        self, client: Optional[redis.Redis] = None, url: Optional[str] = None
    ) -> None:
        self._client = client or redis.from_url(
            url or settings.redis_url, decode_responses=True
        )

    def get(self, key: str) -> Optional[str]:
        return self._client.get(key)

    def set(self, key: str, value: str, ttl_seconds: Optional[int] = None) -> None:
        self._client.set(key, value, ex=ttl_seconds)

    def delete(self, key: str) -> None:
        self._client.delete(key)
