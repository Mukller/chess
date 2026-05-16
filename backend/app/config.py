from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_log_level: str = "INFO"
    app_secret_key: str = Field(default="change-me", min_length=8)

    jwt_algorithm: str = "HS256"
    jwt_expires_minutes: int = 24 * 60

    telegram_bot_token: str = ""
    telegram_bot_username: str = ""
    telegram_webapp_url: str = ""

    redis_url: str = "redis://localhost:6379/0"
    redis_game_ttl_seconds: int = 24 * 60 * 60

    stockfish_path: str = "/usr/games/stockfish"
    stockfish_workers: int = 4
    stockfish_threads: int = 1
    stockfish_hash_mb: int = 32

    cors_origins: List[str] = Field(default_factory=lambda: ["http://localhost:3000"])

    rate_limit_per_minute: int = 30

    @field_validator("cors_origins", mode="before")
    @classmethod
    def split_cors(cls, value):
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
