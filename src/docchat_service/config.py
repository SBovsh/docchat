import os
from logging import DEBUG, INFO

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

load_dotenv()


class BaseAppSettings(BaseSettings):
    local: bool = Field(validation_alias="LOCAL", default=True)  # Всегда локальный режим
    debug: bool = Field(validation_alias="DEBUG", default=False)


class AppSettings(BaseAppSettings):
    app_host: str = Field(validation_alias="APP_HOST", default="0.0.0.0")
    app_port: int = Field(validation_alias="APP_PORT", default=8000)  # Стандартный порт FastAPI
    timezone: str = Field(validation_alias="TIMEZONE", default="UTC")


class LogSettings(BaseAppSettings):
    log_level: str = Field(validation_alias="LOG_LEVEL", default="INFO")

    @property
    def log_lvl(self) -> int:
        return DEBUG if self.debug or self.log_level == "DEBUG" else INFO


class Secrets:
    app: AppSettings = AppSettings()
    log: LogSettings = LogSettings()


APP_CONFIG = Secrets()

__all__ = ["Secrets", "APP_CONFIG"]