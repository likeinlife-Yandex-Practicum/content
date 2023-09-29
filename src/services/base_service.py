from .cache_service.api_cache_service import AsyncApiCacheService
from .search_service import AsyncElasticService


class BaseService:
    """Базовый класс сервисов."""

    def __init__(self, cache_service: AsyncApiCacheService, elastic_service: AsyncElasticService):
        self.cache_service = cache_service
        self.elastic_service = elastic_service
