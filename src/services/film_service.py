from functools import lru_cache

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from orjson import orjson
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis
from enums import EsIndex
from models.es.film_es import FilmEs

from .base_service import BaseService
from .constants import CACHE_EXPIRE_IN_SECONDS


class FilmService(BaseService):

    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        super().__init__(redis, elastic)

    async def get_film_list(
        self,
        genre: str | None,
        query: str | None,
        sort: str | None,
        size: int,
        page: int,
    ) -> list[FilmEs] | None:
        redis_key = self.generate_redis_key(genre, query, sort, size, page)

        body = {
            'size': size,
            'from': (page - 1) * size,
        }
        if query:
            match = {'match': {'title': query}}
        else:
            match = {'match_all': {}}

        body.update({'query': {'bool': {'must': [match]}}})

        if genre:
            body['query']['bool'].update(
                {'filter': {
                    'nested': {
                        'path': 'genre',
                        'query': {
                            'term': {
                                'genre.id': genre
                            }
                        }
                    }
                }})

        if sort:
            order = 'desc' if sort.startswith('-') else 'asc'
            sort = sort.lstrip('-')
            sorting = [{sort: {'order': order}}]
            body.update({'sort': sorting})

        # Пытаемся получить данные из кеша, потому что оно работает быстрее
        film_list = await self._get_film_list_from_cache(redis_key)
        if not film_list:
            film_es_response = await self.elastic.search(
                index=EsIndex.MOVIE,
                body=body,
            )
            if not film_es_response:
                return None
            film_list = [FilmEs(**item['_source']) for item in film_es_response['hits']['hits']]
            await self._put_film_list_to_cache(redis_key, film_list)
        return film_list

    async def get_by_id(self, film_id: str) -> FilmEs | None:
        """Получить фильм по айди."""
        film = await self._film_from_cache(film_id)
        if not film:
            film = await self._get_film_from_elastic(film_id)
            if not film:
                return None
            await self._put_film_to_cache(film)

        return film

    async def _get_film_from_elastic(self, film_id: str) -> FilmEs | None:
        try:
            doc = await self.elastic.get(index=EsIndex.MOVIE, id=film_id)
        except NotFoundError:
            return None
        return FilmEs(**doc['_source'])

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
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
