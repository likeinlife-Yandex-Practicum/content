import hashlib
from typing import Any, Collection, Generic, TypeVar

import orjson
from fastapi.encoders import jsonable_encoder

from models.shared.orjson_base_model import OrjsonBaseModel

from .base_cache_service import BaseAsyncCacheService

M = TypeVar('M', bound=OrjsonBaseModel)


class AsyncApiCacheService(Generic[M]):

    def __init__(self, cache_service: BaseAsyncCacheService, model: type[M]) -> None:
        self.cache_service = cache_service
        self.model = model

    async def get_by_id(self, _id: str) -> M | None:
        data = await self.cache_service.get(_id)
        if not data:
            return None
        return self.model.parse_raw(data)

    async def put_by_id(self, _id: str, value: M) -> None:
        await self.cache_service.put(_id, value.json())

    async def get_by_query(self, query_params: Collection) -> list[M] | None:
        key = self._generate_key(*query_params)
        data = await self.cache_service.get(key)
        if not data:
            return None
        return [self.model(**i) for i in orjson.loads(data)]

    async def put_by_query(self, query_params: Collection, value: list[M]) -> None:
        key = self._generate_key(*query_params)
        await self.cache_service.put(
            key,
            orjson.dumps(jsonable_encoder(value)),
        )

    @staticmethod
    def _generate_key(*args: Any) -> str:
        """Генерация md5-хеша из значений переданных аргументов."""
        return hashlib.md5(str(args).encode('utf-8')).hexdigest()
