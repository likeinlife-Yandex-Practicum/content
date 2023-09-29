from functools import lru_cache

from fastapi import Depends

from enums import EsIndex
from models.es.genre_es import GenreEs

from .base_service import BaseService
from .cache_service import (
    AsyncApiCacheService,
    AsyncRedisCacheService,
    get_redis_service,
)
from .misc.enums import QueryRoute
from .search_service import AsyncElasticService, get_elastic_service


class GenreService(BaseService):
    cache_service: AsyncApiCacheService[GenreEs]

    async def get_by_query(self) -> list[GenreEs] | None:
        query_params = (QueryRoute.GENRE_LIST,)

        from_cache = await self.cache_service.get_by_query(query_params)
        if from_cache:
            return from_cache

        genre_es_response = await self.elastic_service.get_list(index=EsIndex.GENRE, size=100)
        if not genre_es_response:
            return None

        genre_list = [GenreEs(**item) for item in genre_es_response]
        await self.cache_service.put_by_query(query_params, genre_list)
        return genre_list

    async def get_by_id(self, genre_id: str) -> GenreEs | None:
        from_cache = await self.cache_service.get_by_id(genre_id)
        if from_cache:
            return from_cache

        from_es = await self.elastic_service.get_by_id(_id=genre_id, index=EsIndex.GENRE)
        if not from_es:
            return None

        genre = GenreEs(**from_es)

        await self.cache_service.put_by_id(genre_id, genre)

        return genre


@lru_cache()
def get_genre_service(
        redis_cache_service: AsyncRedisCacheService = Depends(get_redis_service),
        elastic_service: AsyncElasticService = Depends(get_elastic_service),
) -> GenreService:
    api_cache_service = AsyncApiCacheService(redis_cache_service, GenreEs)

    return GenreService(api_cache_service, elastic_service=elastic_service)
