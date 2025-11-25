from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    GATEWAY_API_KEY: str
    GATEWAY_URL: str
    GATEWAY_REQUEST_ENDPOINT: str
    REQUEST_TIMEOUT: float = 30.0

    LOGS_LEVEL: str = "DEBUG"

    DEBUG_MODE: bool
    DEBUG_HTTP: bool
    LOGS_LEVEL: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()  # noqa
