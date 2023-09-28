from functools import lru_cache

from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from orjson import orjson  # type: ignore
from redis.asyncio import Redis

from db.redis import get_redis
from enums import EsIndex
from models.es.film_es import FilmEs

from .base_service import BaseService
from .constants import CACHE_EXPIRE_IN_SECONDS
from .query_maker import FilmQueryMaker
from .search_service import AsyncElasticService, get_elastic_service


class FilmService(BaseService):

    async def get_film_list(
        self,
        genre: str | None,
        query: str | None,
        sort: str | None,
        size: int,
        page: int,
    ) -> list[FilmEs] | None:
        redis_key = self.generate_redis_key(genre, query, sort, size, page)

        from_cache = await self._get_film_list_from_cache(redis_key)
        if from_cache:
            return from_cache

        query_maker = FilmQueryMaker(genre_id=genre, title=query)
        from_es = await self.elastic_service.get_list(
            index=EsIndex.MOVIE,
            query_maker=query_maker,
            sort=sort,
            size=size,
            page=page,
        )
        if not from_es:
            return None
        film_list = [FilmEs(**item) for item in from_es]
        await self._put_film_list_to_cache(redis_key, film_list)
        return film_list

    async def get_by_id(self, film_id: str) -> FilmEs | None:
        from_cache = await self._film_from_cache(film_id)

        if from_cache:
            return from_cache

        from_es = await self.elastic_service.get_by_id(
            _id=film_id,
            index=EsIndex.MOVIE,
        )

        if not from_es:
            return None

        film = FilmEs(**from_es)
        await self._put_film_to_cache(film)
        return film

    async def _film_from_cache(self, film_id: str) -> FilmEs | None:
        """Сохранить фильм из кэша."""
        data = await self.redis.get(film_id)
        if not data:
            return None
        film = FilmEs.parse_raw(data)
        return film

    async def _put_film_to_cache(self, film: FilmEs):
        """Сохранить фильм в кэш."""
        await self.redis.set(str(film.id), film.json(), CACHE_EXPIRE_IN_SECONDS)

    async def _get_film_list_from_cache(self, redis_key: str) -> list[FilmEs] | None:
        """Получить список фильмов из кэша."""
        data = await self.redis.get(redis_key)
        if not data:
            return None
        data = orjson.loads(data)
        film_list = [FilmEs(**item) for item in data]
        return film_list

    async def _put_film_list_to_cache(self, redis_key: str, film_list: list[FilmEs]):
        """Сохранить список фильмов в кэш."""
        await self.redis.set(
            redis_key,
            orjson.dumps(jsonable_encoder(film_list)),
            CACHE_EXPIRE_IN_SECONDS,
        )


@lru_cache()
def get_film_service(
        redis: Redis = Depends(get_redis),
        elastic_service: AsyncElasticService = Depends(get_elastic_service),
) -> FilmService:
    return FilmService(redis, elastic_service=elastic_service)
