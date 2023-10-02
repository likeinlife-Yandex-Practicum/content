import abc
from typing import Any


class BaseCacheClient(abc.ABC):

    @abc.abstractmethod
    async def get(self, key: Any) -> Any:
        ...

    @abc.abstractmethod
    async def put(self, key: Any, value: Any) -> None:
        ...
