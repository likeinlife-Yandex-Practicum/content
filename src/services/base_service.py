import hashlib
from typing import Any

from elasticsearch import AsyncElasticsearch
from redis.asyncio import Redis


class BaseService:
    """Базовый класс сервисов."""

    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    @staticmethod
    def generate_redis_key(*args: Any) -> str:
        """Генерация md5-хеша из значений переданных аргументов."""
        return hashlib.md5(str(args).encode('utf-8')).hexdigest()
