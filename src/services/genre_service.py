from functools import lru_cache

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from orjson import orjson
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis
from enums import EsIndex
from models.es.genre_es import GenreEs

from .base_service import BaseService
from .constants import CACHE_EXPIRE_IN_SECONDS


class GenreService(BaseService):

    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        super().__init__(redis, elastic)

    async def get_genre_list(self) -> list[GenreEs]:
        redis_key = self.generate_redis_key('genre_list')

        genre_list = await self._get_genre_list_from_cache(redis_key)
        if not genre_list:
            genre_es_response = await self.elastic.search(index=EsIndex.GENRE, size=1000)
            if not genre_es_response:
                return None
            genre_list = [GenreEs(**item['_source']) for item in genre_es_response['hits']['hits']]
            await self._put_genre_list_to_cache(redis_key, genre_list)
        return genre_list

    async def get_by_id(self, genre_id: str) -> GenreEs | None:
        genre = await self._get_genre_from_cache(genre_id)
        if not genre:
            genre = await self._get_genre_from_elastic(genre_id)
            if not genre:
                return None
            await self._put_genre_to_cache(genre)

        return genre

    async def _get_genre_from_elastic(self, genre_id: str) -> GenreEs | None:
        try:
            doc = await self.elastic.get(index=EsIndex.GENRE, id=genre_id)
        except NotFoundError:
            return None
        return GenreEs(**doc['_source'])

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
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis, elastic)
