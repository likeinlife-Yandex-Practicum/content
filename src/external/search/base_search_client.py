from abc import ABC, abstractmethod


class BaseSearchClient(ABC):

    @abstractmethod
    async def get_by_id(
        self,
        id_: str,
        index_: str,
    ) -> dict | None:
        """Get entity by id."""

    @abstractmethod
    async def get_by_query(
        self,
        index_: str,
        query: dict | None = None,
        sort: list | None = None,
        size: int | None = None,
        from_: int | None = None,
    ) -> list[dict] | None:
        """Get entity list by query."""
