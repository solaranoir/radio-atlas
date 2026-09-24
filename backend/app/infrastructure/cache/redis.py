from functools import lru_cache

from redis import Redis

from app.config import get_settings


@lru_cache
def get_redis_client() -> Redis:
    settings = get_settings()

    return Redis.from_url(
        settings.radio_atlas_redis_url,
        decode_responses=True,
    )
