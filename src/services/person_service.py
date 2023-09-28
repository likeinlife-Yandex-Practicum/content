from functools import lru_cache

from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from orjson import orjson  # type: ignore
from redis.asyncio import Redis

from db.redis import get_redis
from enums import EsIndex
from models.es.person_es import PersonEs
from services.query_maker import PersonQueryMaker
from services.search_service import AsyncElasticService, get_elastic_service

from .base_service import BaseService
from .constants import CACHE_EXPIRE_IN_SECONDS


class PersonService(BaseService):

    async def get_person_list(
        self,
        query: str | None,
        size: int,
        page: int,
    ) -> list[PersonEs] | None:
        redis_key = self.generate_redis_key(query, size, page)

        from_cache = await self._get_person_list_from_cache(redis_key)

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
        await self._put_person_list_to_cache(redis_key, person_list)
        return person_list

    async def get_by_id(self, person_id: str) -> PersonEs | None:
        from_cache = await self._get_person_from_cache(person_id)
        if from_cache:
            return from_cache
        from_es = await self.elastic_service.get_by_id(_id=person_id, index=EsIndex.PERSON)

        if not from_es:
            return None

        person = PersonEs(**from_es)
        await self._put_person_to_cache(person)

        return person

    async def _get_person_from_cache(self, person_id: str) -> PersonEs | None:
        """Получить персону из кэша."""
        data = await self.redis.get(person_id)
        if not data:
            return None
        person = PersonEs.parse_raw(data)
        return person

    async def _put_person_to_cache(self, person: PersonEs):
        """Сохранить персону в кэш."""
        await self.redis.set(str(person.id), person.json(), CACHE_EXPIRE_IN_SECONDS)

    async def _get_person_list_from_cache(self, redis_key: str) -> list[PersonEs] | None:
        """Получить список персону из кэша."""
        data = await self.redis.get(redis_key)
        if not data:
            return None
        data = orjson.loads(data)
        person_list = [PersonEs(**item) for item in data]
        return person_list

    async def _put_person_list_to_cache(self, redis_key: str, person_list: list[PersonEs]):
        """Сохранить список персон в кэш."""
        await self.redis.set(
            redis_key,
            orjson.dumps(jsonable_encoder(person_list)),
            CACHE_EXPIRE_IN_SECONDS,
        )


@lru_cache()
def get_person_service(
        redis: Redis = Depends(get_redis),
        elastic_service: AsyncElasticService = Depends(get_elastic_service),
) -> PersonService:
    return PersonService(redis, elastic_service=elastic_service)
