from pathlib import Path

from pydantic import BaseSettings, Field

BASE_DIR = Path(__file__).parent.parent


class TestSettings(BaseSettings):
    service_url: str = Field('http://localhost:8000', env='FASTAPI_URL')

    es_host: str = Field('127.0.0.1', env='ELASTIC_HOST')
    es_port: str = Field(9200, env='ELASTIC_PORT')
    es_id_field: str = Field('id')
    es_index_mapping: dict = {}

    redis_host: str = Field('127.0.0.1', env='REDIS_HOST')
    redis_port: str = Field(6379, env='REDIS_PORT')

    class Config:
        env_file = '.env'


test_settings = TestSettings()
