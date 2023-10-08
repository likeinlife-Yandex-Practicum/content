import pytest_asyncio
from functional.testdata.es_mapping import ES_MAPPING
from functional.utils.helpers import data_helper

from tests.functional.testdata.enums.es_index import EsIndex


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
