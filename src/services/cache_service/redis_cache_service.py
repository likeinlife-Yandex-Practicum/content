from functools import lru_cache
from typing import Any

from fastapi import Depends
from redis.asyncio import Redis

from db.redis import get_redis
from services.misc.constants import CACHE_EXPIRE_IN_SECONDS

from .base_cache_service import BaseAsyncCacheService


class AsyncRedisCacheService(BaseAsyncCacheService):

    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    async def get(self, key: Any) -> Any:
        return await self.redis.get(key)

    async def put(self, key: Any, value: Any) -> None:
        await self.redis.set(
            key,
            value,
            CACHE_EXPIRE_IN_SECONDS,
        )


@lru_cache()
def get_redis_service(redis: Redis = Depends(get_redis)) -> AsyncRedisCacheService:
    return AsyncRedisCacheService(redis)
