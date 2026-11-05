import pytest
from pydantic import ValidationError

from app.config import MIN_SPOT_RETENTION_DAYS, Settings

DB = "postgresql://localhost/test"


def test_topics_default_to_20m_ft8_and_retention_to_14_days() -> None:
    settings = Settings(radio_atlas_database_url=DB)

    assert settings.psk_reporter_mqtt_topics == ["pskr/filter/v2/20m/FT8/#"]
    assert settings.radio_atlas_spot_retention_days == 14


def test_topics_parse_from_json_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(
        "PSK_REPORTER_MQTT_TOPICS",
        '["pskr/filter/v2/+/FT8/#", " pskr/filter/v2/+/FT4/# "]',
    )

    settings = Settings(radio_atlas_database_url=DB)

    assert settings.psk_reporter_mqtt_topics == [
        "pskr/filter/v2/+/FT8/#",
        "pskr/filter/v2/+/FT4/#",
    ]


@pytest.mark.parametrize("topics", [[], ["", "  "]])
def test_topics_must_not_be_empty(topics: list[str]) -> None:
    with pytest.raises(ValidationError):
        Settings(radio_atlas_database_url=DB, psk_reporter_mqtt_topics=topics)


@pytest.mark.parametrize("days", [0, MIN_SPOT_RETENTION_DAYS, 30])
def test_retention_accepts_disabled_or_safe_windows(days: int) -> None:
    settings = Settings(radio_atlas_database_url=DB, radio_atlas_spot_retention_days=days)

    assert settings.radio_atlas_spot_retention_days == days


@pytest.mark.parametrize("days", [-1, 1, MIN_SPOT_RETENTION_DAYS - 1])
def test_retention_rejects_windows_overlapping_aggregation(days: int) -> None:
    with pytest.raises(ValidationError):
        Settings(radio_atlas_database_url=DB, radio_atlas_spot_retention_days=days)
