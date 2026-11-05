from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[2]

# Incremental aggregation re-covers the last 2 days; retention stays clear of it.
MIN_SPOT_RETENTION_DAYS = 3


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    radio_atlas_cors_origins: list[str] = ["http://localhost:5173"]
    radio_atlas_ingestion_enabled: bool = True
    radio_atlas_aggregation_enabled: bool = False

    @field_validator("radio_atlas_database_url", mode="before")
    @classmethod
    def use_psycopg_driver(cls, value: str) -> str:
        for prefix in ("postgres://", "postgresql://"):
            if value.startswith(prefix):
                return "postgresql+psycopg://" + value[len(prefix) :]
        return value

    radio_atlas_env: str = "development"
    radio_atlas_log_level: str = "INFO"
    radio_atlas_database_url: str
    radio_atlas_redis_url: str = "redis://localhost:6379/0"
    radio_atlas_replay_session_ttl_seconds: int = 86400
    noaa_base_url: str = "https://services.swpc.noaa.gov"
    psk_reporter_base_url: str = ""
    psk_reporter_mqtt_host: str = "mqtt.pskreporter.info"
    psk_reporter_mqtt_port: int = 1883
    # JSON list in the environment, for example:
    # PSK_REPORTER_MQTT_TOPICS='["pskr/filter/v2/+/FT8/#","pskr/filter/v2/+/FT4/#"]'
    psk_reporter_mqtt_topics: list[str] = ["pskr/filter/v2/20m/FT8/#"]
    # Raw spots older than this many days are rolled up and then deleted.
    # 0 disables retention. Must leave at least MIN_SPOT_RETENTION_DAYS so the
    # retention job never overlaps the incremental aggregation window.
    radio_atlas_spot_retention_days: int = 14

    @field_validator("psk_reporter_mqtt_topics")
    @classmethod
    def require_topics(cls, value: list[str]) -> list[str]:
        topics = [topic.strip() for topic in value if topic.strip()]
        if not topics:
            raise ValueError("At least one PSK Reporter MQTT topic is required")
        return topics

    @field_validator("radio_atlas_spot_retention_days")
    @classmethod
    def validate_retention(cls, value: int) -> int:
        if value != 0 and value < MIN_SPOT_RETENTION_DAYS:
            raise ValueError(
                f"Spot retention must be 0 (disabled) or at least {MIN_SPOT_RETENTION_DAYS} days"
            )
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
