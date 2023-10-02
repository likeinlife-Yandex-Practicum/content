from external.cache.api_cache_adapter import ApiCacheAdapter
from external.search import ElasticClient


class BaseService:
    """Базовый класс сервисов."""

    def __init__(self, cache_service: ApiCacheAdapter, elastic_service: ElasticClient):
        self.cache_service = cache_service
        self.elastic_service = elastic_service
