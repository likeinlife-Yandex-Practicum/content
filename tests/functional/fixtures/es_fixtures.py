import pytest_asyncio
from elasticsearch import AsyncElasticsearch
from functional.settings import test_settings


@pytest_asyncio.fixture(scope='session')
async def es_client():
    client = AsyncElasticsearch(
        hosts=f'{test_settings.es_host}:{test_settings.es_port}',
        validate_cert=False,
        use_ssl=False,
    )
    yield client
    await client.close()
