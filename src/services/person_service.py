from functools import lru_cache

from fastapi import Depends

from enums import EsIndex
from models.es.person_es import PersonEs

from .base_service import BaseService
from .cache_service import (
    AsyncApiCacheService,
    AsyncRedisCacheService,
    get_redis_service,
)
from .misc.enums import QueryRoute
from .misc.query_maker import PersonQueryMaker
from .search_service import AsyncElasticService, get_elastic_service


class PersonService(BaseService):
    cache_service: AsyncApiCacheService[PersonEs]

    async def get_by_query(
        self,
        query: str | None,
        size: int,
        page: int,
    ) -> list[PersonEs] | None:
        query_parameters = (QueryRoute.PERSON_LIST, query, size, page)

        from_cache = await self.cache_service.get_by_query(query_parameters)

        if from_cache:
            return from_cache

        query_maker = PersonQueryMaker(query)
        person_es_response = await self.elastic_service.get_list(
            index=EsIndex.PERSON,
            query_maker=query_maker,
            size=size,
            page=page,
        )
        if not person_es_response:
            return None

        person_list = [PersonEs(**item) for item in person_es_response]
        await self.cache_service.put_by_query(query_parameters, person_list)
        return person_list

    async def get_by_id(self, person_id: str) -> PersonEs | None:
        from_cache = await self.cache_service.get_by_id(person_id)
        if from_cache:
            return from_cache
        from_es = await self.elastic_service.get_by_id(_id=person_id, index=EsIndex.PERSON)

        if not from_es:
            return None

        person = PersonEs(**from_es)
        await self.cache_service.put_by_id(person_id, person)

        return person


@lru_cache()
def get_person_service(
        redis_cache_service: AsyncRedisCacheService = Depends(get_redis_service),
        elastic_service: AsyncElasticService = Depends(get_elastic_service),
) -> PersonService:
    api_cache_service = AsyncApiCacheService(redis_cache_service, PersonEs)

    return PersonService(api_cache_service, elastic_service=elastic_service)
