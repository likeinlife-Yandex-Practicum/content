from functools import lru_cache

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from orjson import orjson
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis
from enums import EsIndex
from models.es.person_es import PersonEs

from .base_service import BaseService
from .constants import CACHE_EXPIRE_IN_SECONDS


class PersonService(BaseService):

    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        super().__init__(redis, elastic)

    async def get_person_list(
        self,
        query: str | None,
        size: int,
        page: int,
    ) -> list[PersonEs] | None:
        redis_key = self.generate_redis_key(query, size, page)

        body = {
            'size': size,
            'from': (page - 1) * size,
        }
        match = {'match': {'name': query}}

        body.update({'query': {'bool': {'must': [match]}}})

        person_list = await self._get_person_list_from_cache(redis_key)
        if not person_list:
            person_es_response = await self.elastic.search(
                index=EsIndex.PERSON,
                body=body,
            )
            if not person_es_response:
                return None
            person_list = [PersonEs(**item['_source']) for item in person_es_response['hits']['hits']]
            await self._put_person_list_to_cache(redis_key, person_list)
        return person_list

    async def get_by_id(self, person_id: str) -> PersonEs | None:
        person = await self._get_person_from_cache(person_id)
        if not person:
            person = await self._get_person_from_elastic(person_id)
            if not person:
                return None
            await self._put_person_to_cache(person)

        return person

    async def _get_person_from_elastic(self, person_id: str) -> PersonEs | None:
        try:
            doc = await self.elastic.get(index=EsIndex.PERSON, id=person_id)
        except NotFoundError:
            return None
        return PersonEs(**doc['_source'])

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
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
