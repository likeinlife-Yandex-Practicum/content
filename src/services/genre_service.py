from functools import lru_cache

from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from orjson import orjson  # type: ignore
from redis.asyncio import Redis

from db.redis import get_redis
from enums import EsIndex
from models.es.genre_es import GenreEs
from services.search_service import AsyncElasticService, get_elastic_service

from .base_service import BaseService
from .constants import CACHE_EXPIRE_IN_SECONDS


class GenreService(BaseService):

    async def get_genre_list(self) -> list[GenreEs] | None:
        redis_key = self.generate_redis_key('genre_list')

        from_cache = await self._get_genre_list_from_cache(redis_key)
        if from_cache:
            return from_cache

        genre_es_response = await self.elastic_service.get_list(index=EsIndex.GENRE, size=100)
        if not genre_es_response:
            return None

        genre_list = [GenreEs(**item) for item in genre_es_response]
        await self._put_genre_list_to_cache(redis_key=redis_key, genre_list=genre_list)
        return genre_list

    async def get_by_id(self, genre_id: str) -> GenreEs | None:
        from_cache = await self._get_genre_from_cache(genre_id)
        if from_cache:
            return from_cache

        from_es = await self.elastic_service.get_by_id(_id=genre_id, index=EsIndex.GENRE)
        if not from_es:
            return None

        genre = GenreEs(**from_es)

        await self._put_genre_to_cache(genre)

        return genre

    async def _get_genre_from_cache(self, genre_id: str) -> GenreEs | None:
        """Получить персону из кэша."""
        data = await self.redis.get(genre_id)
        if not data:
            return None
        genre = GenreEs.parse_raw(data)
        return genre

    async def _put_genre_to_cache(self, genre: GenreEs):
        """Сохранить персону в кэш."""
        await self.redis.set(str(genre.id), genre.json(), CACHE_EXPIRE_IN_SECONDS)

    async def _get_genre_list_from_cache(self, redis_key: str) -> list[GenreEs] | None:
        """Получить список персону из кэша."""
        data = await self.redis.get(redis_key)
        if not data:
            return None
        data = orjson.loads(data)
        genre_list = [GenreEs(**item) for item in data]
        return genre_list

    async def _put_genre_list_to_cache(self, redis_key: str, genre_list: list[GenreEs]):
        """Сохранить список персон в кэш."""
        await self.redis.set(
            redis_key,
            orjson.dumps(jsonable_encoder(genre_list)),
            CACHE_EXPIRE_IN_SECONDS,
        )


@lru_cache()
def get_genre_service(
        redis: Redis = Depends(get_redis),
        elastic_service: AsyncElasticService = Depends(get_elastic_service),
) -> GenreService:
    return GenreService(redis, elastic_service=elastic_service)
