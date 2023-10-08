from functools import lru_cache

from fastapi import Depends

from enums import EsIndex
from external.cache import ApiCacheAdapter, RedisCacheClient, get_redis_client
from external.search import (
    ApiSearchAdapter,
    ElasticSearchClient,
    get_elastic_client,
)
from models.es.film_es import FilmEs

from .base_service import BaseService
from .misc.enums import QueryRoute
from .misc.query_maker import FilmQueryMaker


class FilmService(BaseService):
    cache_adapter: ApiCacheAdapter[FilmEs]
    search_adapter: ApiSearchAdapter[FilmEs]

    async def get_by_query(
        self,
        genre: str | None,
        query: str | None,
        sort: str | None,
        size: int,
        page: int,
    ) -> list[FilmEs] | None:
        query_parameters = (QueryRoute.FILM_LIST, genre, query, sort, size, page)
        from_cache = await self.cache_adapter.get_by_query(query_parameters)
        if from_cache:
            return from_cache

        query_maker = FilmQueryMaker(genre_id=genre, title=query)
        from_es = await self.search_adapter.get_by_query(
            index_=EsIndex.MOVIE,
            query_maker=query_maker,
            sort=sort,
            size=size,
            page=page,
        )
        if not from_es:
            return None

        await self.cache_adapter.put_by_query(query_parameters, from_es)
        return from_es

    async def get_by_id(self, film_id: str) -> FilmEs | None:
        from_cache = await self.cache_adapter.get_by_id(film_id)

        if from_cache:
            return from_cache

        from_es = await self.search_adapter.get_by_id(
            id_=film_id,
            index_=EsIndex.MOVIE,
        )

        if not from_es:
            return None

        await self.cache_adapter.put_by_id(film_id, from_es)
        return from_es


@lru_cache()
def get_film_service(
        cache_client: RedisCacheClient = Depends(get_redis_client),
        search_client: ElasticSearchClient = Depends(get_elastic_client),
) -> FilmService:
    cache_adapter = ApiCacheAdapter(cache_client, FilmEs)
    search_adapter = ApiSearchAdapter(search_client, FilmEs)

    return FilmService(cache_adapter, search_adapter=search_adapter)
