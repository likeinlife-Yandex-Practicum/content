import asyncio

import aiohttp
import aioredis
import pytest
import pytest_asyncio
from elasticsearch import AsyncElasticsearch

from functional.settings import test_settings
from functional.testdata.es_mapping import ES_MAPPING
from functional.utils.helpers import data_helper
from tests.functional.testdata.enums.es_index import EsIndex


@pytest.fixture(scope='session')
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope='session')
async def es_client():
    client = AsyncElasticsearch(
        hosts=f'{test_settings.es_host}:{test_settings.es_port}',
        validate_cert=False,
        use_ssl=False
    )
    yield client
    await client.close()


@pytest_asyncio.fixture(scope='function')
async def redis_client():
    redis = await aioredis.from_url(f'redis://{test_settings.redis_host}:{test_settings.redis_port}')
    await redis.flushall(asynchronous=True)
    yield redis
    await redis.close()


@pytest_asyncio.fixture(scope='session', autouse=True)
async def prepare_test_data(es_client):
    """Загрузка тестовых данных из дампа."""
    # создаем индексы
    for _index in list(EsIndex):
        if await es_client.indices.exists(index=_index):
            await es_client.indices.delete(index=_index)
    for key, value in ES_MAPPING.items():
        await es_client.indices.create(
            index=key,
            settings=value['settings'],
            mappings=value['mappings'],
        )
    # загружаем данные
    await data_helper.create_test_data(es_client)
    yield
    # удаляем все индексы и данные
    for _index in list(EsIndex):
        await es_client.indices.delete(index=_index)


@pytest_asyncio.fixture(scope='session')
async def api_client():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest.fixture
def make_get_request(api_client):
    async def inner(url: str, params: dict = None):
        url = f'{test_settings.service_url}{url}'
        async with api_client.get(url, params=params) as response:
            return await response.json(), response.status

    return inner
