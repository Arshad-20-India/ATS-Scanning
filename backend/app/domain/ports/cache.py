"""
Generic cache port. Deliberately minimal (get/set/delete on string
keys/values) so it stays swappable -- Redis is the Phase 5 adapter,
but an in-memory or Memcached adapter could implement this identically.

Values are always strings; callers are responsible for
serialization (e.g. json.dumps/loads), which keeps this interface
free of any assumption about what's being cached.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional


class ICache(ABC):
    @abstractmethod
    def get(self, key: str) -> Optional[str]:
        raise NotImplementedError

    @abstractmethod
    def set(self, key: str, value: str, ttl_seconds: Optional[int] = None) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete(self, key: str) -> None:
        raise NotImplementedError
