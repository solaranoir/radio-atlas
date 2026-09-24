import json
from typing import Any

from redis import Redis


class StatisticsCache:
    def __init__(
        self,
        redis_client: Redis,
        *,
        ttl_seconds: int = 300,
    ) -> None:
        self._redis = redis_client
        self._ttl_seconds = ttl_seconds

    def get(self, key: str) -> dict[str, Any] | None:
        cached = self._redis.get(key)

        if cached is None:
            return None

        value = json.loads(cached)

        if not isinstance(value, dict):
            return None

        return value

    def set(self, key: str, value: dict[str, Any]) -> None:
        self._redis.setex(
            key,
            self._ttl_seconds,
            json.dumps(value),
        )
