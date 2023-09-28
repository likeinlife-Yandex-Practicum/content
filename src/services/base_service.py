import hashlib
from typing import Any

from redis.asyncio import Redis

from .search_service import AsyncElasticService


class BaseService:
    """Базовый класс сервисов."""

    def __init__(self, redis: Redis, elastic_service: AsyncElasticService):
        self.redis = redis
        self.elastic_service = elastic_service

    @staticmethod
    def generate_redis_key(*args: Any) -> str:
        """Генерация md5-хеша из значений переданных аргументов."""
        return hashlib.md5(str(args).encode('utf-8')).hexdigest()
