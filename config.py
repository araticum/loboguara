import os
from urllib.parse import urlparse, urlunparse


def _build_redis_url_with_db(redis_url: str, redis_db: int) -> str:
    parsed = urlparse(redis_url)
    normalized_path = f"/{redis_db}"
    return urlunparse(
        (
            parsed.scheme,
            parsed.netloc,
            normalized_path,
            parsed.params,
            parsed.query,
            parsed.fragment,
        )
    )


DB_SCHEMA = os.getenv("SERIEMA_DB_SCHEMA", "seriema")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/eventsaas",
)

REDIS_DB = int(os.getenv("SERIEMA_REDIS_DB", "5"))
RAW_REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
REDIS_URL = _build_redis_url_with_db(RAW_REDIS_URL, REDIS_DB)

REDIS_KEY_PREFIX = os.getenv("SERIEMA_REDIS_KEY_PREFIX", "seriema")
QUEUE_PREFIX = os.getenv("SERIEMA_QUEUE_PREFIX", "queue:seriema")

APP_BASE_URL = os.getenv("APP_BASE_URL", "https://api.event-saas.com")


def queue_name(suffix: str) -> str:
    normalized = suffix.strip(":")
    return f"{QUEUE_PREFIX}:{normalized}"


def prefixed_redis_key(key: str) -> str:
    if not key:
        return REDIS_KEY_PREFIX
    return f"{REDIS_KEY_PREFIX}:{key}"
