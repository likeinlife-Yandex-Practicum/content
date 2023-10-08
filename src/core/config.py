from logging import config as logging_config
from pathlib import Path

from pydantic import BaseSettings, Field

from core.logger import get_logging_settings


class Settings(BaseSettings):
    project_name: str = Field('movies')
    redis_host: str = Field('127.0.0.1')
    redis_port: int = Field(6379)
    elastic_host: str = Field('127.0.0.1')
    elastic_port: int = Field(9200)

    logging_level: str = Field('INFO')
    console_logging_level: str = Field('DEBUG')
    backoff_max_time: float = Field(5.0)

    class Config:
        env_file = '.env'


BASE_DIR = Path(__file__).parent.parent
settings = Settings()  # type: ignore

logging_config.dictConfig(get_logging_settings(
    settings.logging_level,
    settings.console_logging_level,
))
