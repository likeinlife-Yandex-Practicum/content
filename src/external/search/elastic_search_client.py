from functools import lru_cache

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends

from db.elastic import get_elastic

from .base_search_client import BaseSearchClient


class ElasticSearchClient(BaseSearchClient):

    def __init__(self, elastic: AsyncElasticsearch) -> None:
        self.elastic = elastic

    async def get_by_id(
        self,
        id_: str,
        index_: str,
    ) -> dict | None:
        try:
            doc = await self.elastic.get(index=index_, id=id_)
        except NotFoundError:
            return None
        return doc['_source']

    async def get_by_query(
        self,
        index_: str,
        query: dict | None = None,
        sort: list | None = None,
        size: int | None = None,
        from_: int | None = None,
    ) -> list[dict] | None:
        try:
            doc = await self.elastic.search(
                index=index_,
                query=query,
                sort=sort,  # type: ignore
                from_=from_,
                size=size,
            )
        except NotFoundError:
            return None
        return [obj['_source'] for obj in doc['hits']['hits']]


@lru_cache()
def get_elastic_client(elastic: AsyncElasticsearch = Depends(get_elastic)) -> ElasticSearchClient:
    return ElasticSearchClient(elastic=elastic)
