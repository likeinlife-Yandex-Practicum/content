import aiohttp
import pytest
import pytest_asyncio
from functional.settings import test_settings


@pytest_asyncio.fixture(scope='session')
async def api_client():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest.fixture
def make_get_request(api_client):
    async def inner(url: str, params: dict | None = None):
        url = f'{test_settings.service_url}{url}'
        async with api_client.get(url, params=params) as response:
            return await response.json(), response.status

    return inner
