from typing import Generic, TypeVar

import backoff

from core.config import settings
from models.shared.orjson_base_model import OrjsonBaseModel
from services.misc.query_maker import BaseQueryMaker

from .base_search_client import BaseSearchClient

M = TypeVar('M', bound=OrjsonBaseModel)


class ApiSearchAdapter(Generic[M]):

    def __init__(self, search_client: BaseSearchClient, model: type[M]) -> None:
        self.search_client = search_client
        self.model = model

    @backoff.on_exception(backoff.expo, Exception, max_time=settings.backoff_max_time)
    async def get_by_id(self, id_: str, index_: str) -> M | None:
        data = await self.search_client.get_by_id(id_, index_)
        if not data:
            return None
        return self.model(**data)

    @backoff.on_exception(backoff.expo, Exception, max_time=settings.backoff_max_time)
    async def get_by_query(
        self,
        index_: str,
        size: int,
        query_maker: BaseQueryMaker | None = None,
        sort: str | None = None,
        page: int | None = None,
    ) -> list[M] | None:
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

        data = await self.search_client.get_by_query(
            index_=index_,
            query=query,
            sort=dsl_sort,
            from_=dsl_from,
            size=size,
        )

        if not data:
            return None
        return [self.model(**item) for item in data]
