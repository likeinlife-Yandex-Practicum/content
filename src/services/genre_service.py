from functools import lru_cache

from fastapi import Depends

from enums import EsIndex
from external.cache import ApiCacheAdapter, RedisCacheClient, get_redis_client
from external.search import (
    ApiSearchAdapter,
    ElasticSearchClient,
    get_elastic_client,
)
from models.es.genre_es import GenreEs

from .base_service import BaseService
from .misc.enums import QueryRoute


class GenreService(BaseService):
    cache_adapter: ApiCacheAdapter[GenreEs]
    search_adapter: ApiSearchAdapter[GenreEs]

    async def get_by_query(self) -> list[GenreEs] | None:
        query_params = (QueryRoute.GENRE_LIST,)

        from_cache = await self.cache_adapter.get_by_query(query_params)
        if from_cache:
            return from_cache

        from_es = await self.search_adapter.get_by_query(index_=EsIndex.GENRE, size=100)
        if not from_es:
            return None

        await self.cache_adapter.put_by_query(query_params, from_es)
        return from_es

    async def get_by_id(self, genre_id: str) -> GenreEs | None:
        from_cache = await self.cache_adapter.get_by_id(genre_id)
        if from_cache:
            return from_cache

        from_es = await self.search_adapter.get_by_id(id_=genre_id, index_=EsIndex.GENRE)
        if not from_es:
            return None

        await self.cache_adapter.put_by_id(genre_id, from_es)

        return from_es


@lru_cache()
def get_genre_service(
        cache_client: RedisCacheClient = Depends(get_redis_client),
        search_client: ElasticSearchClient = Depends(get_elastic_client),
) -> GenreService:
    cache_adapter = ApiCacheAdapter(cache_client, GenreEs)
    search_adapter = ApiSearchAdapter(search_client, GenreEs)

    return GenreService(cache_adapter, search_adapter=search_adapter)
