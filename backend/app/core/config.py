"""
Central configuration, read once from environment variables with
sensible defaults. Deliberately framework-free (no pydantic-settings
dependency yet) so it's usable from any layer, including scripts and
Celery workers, without pulling in FastAPI.

This is the single source of truth for values that must stay in sync
across the system (e.g. the similarity threshold used by MatchingPolicy
should be the same value the frontend displays as "match confidence
cutoff" -- both read from here, or from the API's serialization of
this config, never hardcoded separately).
"""

from __future__ import annotations

import os
from dataclasses import dataclass


def _env_float(key: str, default: float) -> float:
    value = os.environ.get(key)
    return float(value) if value is not None else default


def _env_str(key: str, default: str) -> str:
    return os.environ.get(key, default)


def _env_bool(key: str, default: bool) -> bool:
    value = os.environ.get(key)
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")


def _clean_redis_url(url: str) -> str:
    if not url:
        return url
    url = url.strip().strip("'\"")
    # If the user copied the full redis-cli command from Upstash
    if "redis-cli" in url or "-u" in url:
        has_tls = "--tls" in url
        for part in url.split():
            if part.startswith("redis://") or part.startswith("rediss://"):
                url = part
                break
        if has_tls and url.startswith("redis://"):
            url = "rediss://" + url[len("redis://"):]
    elif "upstash.io" in url and url.startswith("redis://"):
        # Upstash always uses TLS
        url = "rediss://" + url[len("redis://"):]
    return url


def _env_redis_url(key: str, default: str) -> str:
    raw = os.environ.get(key)
    if raw is None:
        return default
    return _clean_redis_url(raw)


@dataclass(frozen=True)
class Settings:
    # NLP / embeddings
    spacy_model_name: str = _env_str("SPACY_MODEL_NAME", "en_core_web_sm")
    sentence_transformer_model_name: str = _env_str(
        "SENTENCE_TRANSFORMER_MODEL", "all-MiniLM-L6-v2"
    )
    semantic_similarity_threshold: float = _env_float(
        "SEMANTIC_SIMILARITY_THRESHOLD", 0.55
    )

    # LLM provider (Phase 3)
    llm_provider: str = _env_str("LLM_PROVIDER", "openai")
    llm_model_name: str = _env_str("LLM_MODEL_NAME", "gpt-4o-mini")

    # Persistence (Phase 5)
    database_url: str = _env_str(
        "DATABASE_URL",
        "postgresql+psycopg2://resume_scanner:resume_scanner_dev@localhost:5432/resume_scanner_dev",
    )
    redis_url: str = _env_redis_url("REDIS_URL", "redis://localhost:6379/0")
    embedding_cache_ttl_seconds: int = int(
        _env_str("EMBEDDING_CACHE_TTL_SECONDS", str(60 * 60 * 24 * 7))
    )

    # Auth (Phase 6)
    jwt_secret_key: str = _env_str(
        "JWT_SECRET_KEY", "dev-only-insecure-secret-change-in-production"
    )
    jwt_algorithm: str = _env_str("JWT_ALGORITHM", "HS256")
    jwt_access_token_expire_minutes: int = int(
        _env_str("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60")
    )

    # Celery (Phase 6)
    celery_broker_url: str = _env_redis_url("CELERY_BROKER_URL", "redis://localhost:6379/2")
    celery_result_backend: str = _env_redis_url(
        "CELERY_RESULT_BACKEND", "redis://localhost:6379/2"
    )

    # Observability & hardening (Phase 9)
    environment: str = _env_str("ENVIRONMENT", "development")  # development | production
    cors_allowed_origins: str = _env_str("CORS_ALLOWED_ORIGINS", "*")
    max_upload_size_bytes: int = int(_env_str("MAX_UPLOAD_SIZE_BYTES", str(10 * 1024 * 1024)))
    rate_limit_auth: str = _env_str("RATE_LIMIT_AUTH", "10/minute")
    rate_limit_analysis: str = _env_str("RATE_LIMIT_ANALYSIS", "20/minute")
    rate_limit_default: str = _env_str("RATE_LIMIT_DEFAULT", "120/minute")
    rate_limit_enabled: bool = _env_bool("RATE_LIMIT_ENABLED", True)

    def cors_origins_list(self) -> list[str]:
        if self.cors_allowed_origins.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_allowed_origins.split(",") if origin.strip()]

    def is_production(self) -> bool:
        return self.environment.lower() == "production"


settings = Settings()
