from external.cache.api_cache_adapter import ApiCacheAdapter
from external.search import ApiSearchAdapter


class BaseService:
    """Базовый класс сервисов."""

    def __init__(self, cache_adapter: ApiCacheAdapter, search_adapter: ApiSearchAdapter):
        self.cache_adapter = cache_adapter
        self.search_adapter = search_adapter
