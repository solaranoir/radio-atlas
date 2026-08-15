from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    radio_atlas_env: str = "development"
    radio_atlas_log_level: str = "INFO"
    radio_atlas_database_url: str
    radio_atlas_redis_url: str = "redis://localhost:6379/0"
    noaa_base_url: str = "https://services.swpc.noaa.gov"
    psk_reporter_base_url: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
