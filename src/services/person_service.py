from functools import lru_cache

from fastapi import Depends

from enums import EsIndex
from external.cache import ApiCacheAdapter, RedisCacheClient, get_redis_client
from external.search import (
    ApiSearchAdapter,
    ElasticSearchClient,
    get_elastic_client,
)
from models.es.person_es import PersonEs

from .base_service import BaseService
from .misc.enums import QueryRoute
from .misc.query_maker import PersonQueryMaker


class PersonService(BaseService):
    cache_adapter: ApiCacheAdapter[PersonEs]
    search_adapter: ApiSearchAdapter[PersonEs]

    async def get_by_query(
        self,
        query: str | None,
        size: int,
        page: int,
    ) -> list[PersonEs] | None:
        query_parameters = (QueryRoute.PERSON_LIST, query, size, page)

        from_cache = await self.cache_adapter.get_by_query(query_parameters)

        if from_cache:
            return from_cache

        query_maker = PersonQueryMaker(query)
        from_es = await self.search_adapter.get_by_query(
            index_=EsIndex.PERSON,
            query_maker=query_maker,
            size=size,
            page=page,
        )
        if not from_es:
            return None

        await self.cache_adapter.put_by_query(query_parameters, from_es)
        return from_es

    async def get_by_id(self, person_id: str) -> PersonEs | None:
        from_cache = await self.cache_adapter.get_by_id(person_id)
        if from_cache:
            return from_cache
        from_es = await self.search_adapter.get_by_id(id_=person_id, index_=EsIndex.PERSON)

        if not from_es:
            return None

        await self.cache_adapter.put_by_id(person_id, from_es)

        return from_es


@lru_cache()
def get_person_service(
        cache_client: RedisCacheClient = Depends(get_redis_client),
        search_client: ElasticSearchClient = Depends(get_elastic_client),
) -> PersonService:
    cache_adapter = ApiCacheAdapter(cache_client, PersonEs)
    search_adapter = ApiSearchAdapter(search_client, PersonEs)

    return PersonService(cache_adapter, search_adapter=search_adapter)
