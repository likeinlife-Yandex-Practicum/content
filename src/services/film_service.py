from functools import lru_cache

from fastapi import Depends

from enums import EsIndex
from models.es.film_es import FilmEs

from .base_service import BaseService
from .cache_service import (
    AsyncApiCacheService,
    AsyncRedisCacheService,
    get_redis_service,
)
from .misc.enums import QueryRoute
from .misc.query_maker import FilmQueryMaker
from .search_service import AsyncElasticService, get_elastic_service


class FilmService(BaseService):
    cache_service: AsyncApiCacheService[FilmEs]

    async def get_by_query(
        self,
        genre: str | None,
        query: str | None,
        sort: str | None,
        size: int,
        page: int,
    ) -> list[FilmEs] | None:
        query_parameters = (QueryRoute.FILM_LIST, genre, query, sort, size, page)
        from_cache = await self.cache_service.get_by_query(query_parameters)
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

        await self.cache_service.put_by_query(query_parameters, film_list)
        return film_list

    async def get_by_id(self, film_id: str) -> FilmEs | None:
        from_cache = await self.cache_service.get_by_id(film_id)

        if from_cache:
            return from_cache

        from_es = await self.elastic_service.get_by_id(
            _id=film_id,
            index=EsIndex.MOVIE,
        )

        if not from_es:
            return None

        film = FilmEs(**from_es)
        await self.cache_service.put_by_id(film_id, film)
        return film


@lru_cache()
def get_film_service(
        redis_cache_service: AsyncRedisCacheService = Depends(get_redis_service),
        elastic_service: AsyncElasticService = Depends(get_elastic_service),
) -> FilmService:
    api_cache_service = AsyncApiCacheService(redis_cache_service, FilmEs)

    return FilmService(api_cache_service, elastic_service=elastic_service)
