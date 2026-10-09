from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    radio_atlas_cors_origins: list[str] = ["http://localhost:5173"]
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
    psk_reporter_mqtt_topic: str = "pskr/filter/v2/20m/FT8/#"


@lru_cache
def get_settings() -> Settings:
    return Settings()
