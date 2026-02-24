from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "development"
    debug: bool = False
    log_level: str = "INFO"

    host: str = "0.0.0.0"
    port: int = 8000
    public_url: str = "https://localhost"

    telegram_bot_token: str = ""
    telegram_webhook_secret: str = ""
    private_group_id: int = 0

    database_url: str = postgresql+asyncpg://user:pass@host:5432/db
    redis_url: str = "redis://localhost:6379/0"

    payment_provider: str = "yookassa"
    payment_webhook_secret: str = ""
    payment_api_key: str = ""
    payment_shop_id: str = ""

    celery_broker_url: str = "redis://localhost:6379/1"

    admin_ids: str = ""

    @property
    def admin_ids_list(self) -> List[int]:
        if not self.admin_ids:
            return []
        return [int(x.strip()) for x in self.admin_ids.split(",") if x.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
