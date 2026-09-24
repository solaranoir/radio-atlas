from unittest.mock import Mock

from redis import Redis

from app.analytics.statistics.cache import StatisticsCache


def test_statistics_cache_returns_cached_value() -> None:
    redis_client = Mock(spec=Redis)
    redis_client.get.return_value = '{"observation_count": 120}'

    cache = StatisticsCache(redis_client)

    result = cache.get("statistics:band:20m:FT8")

    assert result == {"observation_count": 120}
    redis_client.get.assert_called_once_with("statistics:band:20m:FT8")


def test_statistics_cache_sets_value_with_ttl() -> None:
    redis_client = Mock(spec=Redis)
    cache = StatisticsCache(redis_client, ttl_seconds=120)

    cache.set(
        "statistics:band:20m:FT8",
        {"observation_count": 120},
    )

    redis_client.setex.assert_called_once_with(
        "statistics:band:20m:FT8",
        120,
        '{"observation_count": 120}',
    )


def test_statistics_cache_returns_none_on_cache_miss() -> None:
    redis_client = Mock(spec=Redis)
    redis_client.get.return_value = None

    cache = StatisticsCache(redis_client)

    result = cache.get("statistics:band:20m:FT8")

    assert result is None
    redis_client.get.assert_called_once_with("statistics:band:20m:FT8")
