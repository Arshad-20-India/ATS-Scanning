from __future__ import annotations

import time

from app.infrastructure.persistence.redis_cache import RedisCache


def test_set_and_get_round_trip(redis_client):
    cache = RedisCache(client=redis_client)
    cache.set("key1", "value1")
    assert cache.get("key1") == "value1"


def test_get_missing_key_returns_none(redis_client):
    cache = RedisCache(client=redis_client)
    assert cache.get("does-not-exist") is None


def test_delete_removes_key(redis_client):
    cache = RedisCache(client=redis_client)
    cache.set("key1", "value1")
    cache.delete("key1")
    assert cache.get("key1") is None


def test_ttl_expires_key(redis_client):
    cache = RedisCache(client=redis_client)
    cache.set("key1", "value1", ttl_seconds=1)
    assert cache.get("key1") == "value1"
    time.sleep(1.5)
    assert cache.get("key1") is None


def test_set_without_ttl_persists(redis_client):
    cache = RedisCache(client=redis_client)
    cache.set("key1", "value1")  # no ttl
    ttl = redis_client.ttl("key1")
    assert ttl == -1  # -1 means "no expiry" in Redis
