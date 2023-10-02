from functools import lru_cache

from fastapi import Depends

from enums import EsIndex
from external.cache import ApiCacheAdapter, RedisCacheClient, get_redis_client
from external.search import ElasticClient, get_elastic_client
from models.es.person_es import PersonEs

from .base_service import BaseService
from .misc.enums import QueryRoute
from .misc.query_maker import PersonQueryMaker


class PersonService(BaseService):
    cache_service: ApiCacheAdapter[PersonEs]

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
        redis_cache_service: RedisCacheClient = Depends(get_redis_client),
        elastic_service: ElasticClient = Depends(get_elastic_client),
) -> PersonService:
    api_cache_service = ApiCacheAdapter(redis_cache_service, PersonEs)

    return PersonService(api_cache_service, elastic_service=elastic_service)
