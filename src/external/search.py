from functools import lru_cache

import backoff
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends

from core.config import settings
from db.elastic import get_elastic
from services.misc.query_maker import BaseQueryMaker


class ElasticClient:

    def __init__(self, elastic: AsyncElasticsearch) -> None:
        self.elastic = elastic

    @backoff.on_exception(backoff.expo, Exception, max_time=settings.backoff_max_time)
    async def get_by_id(
        self,
        _id: str,
        index: str,
    ) -> dict | None:
        try:
            doc = await self.elastic.get(index=index, id=_id)
        except NotFoundError:
            return None
        return doc['_source']

    @backoff.on_exception(backoff.expo, Exception, max_time=settings.backoff_max_time)
    async def get_by_query(
        self,
        index: str,
        query_maker: BaseQueryMaker | None = None,
        sort: str | None = None,
        size: int | None = None,
        page: int | None = None,
    ) -> list[dict] | None:
        if sort:
            _order = 'desc' if sort.startswith('-') else 'asc'
            _sort = sort.lstrip('-')
            dsl_sort = [{_sort: {'order': _order}}]
        else:
            dsl_sort = None

        if page and size:
            dsl_from = (page - 1) * size
        else:
            dsl_from = None

        query = query_maker.get_query() if query_maker else None

        try:
            doc = await self.elastic.search(
                index=index,
                query=query,
                sort=dsl_sort,  # type: ignore
                from_=dsl_from,
                size=size,
            )
        except NotFoundError:
            return None
        return [obj['_source'] for obj in doc['hits']['hits']]


@lru_cache()
def get_elastic_client(elastic: AsyncElasticsearch = Depends(get_elastic)) -> ElasticClient:
    return ElasticClient(elastic=elastic)
