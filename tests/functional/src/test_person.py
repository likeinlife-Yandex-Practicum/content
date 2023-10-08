import json
from http import HTTPStatus

import pytest
from functional.testdata import person_data
from functional.testdata.enums.end_point import EndPoint
from functional.testdata.enums.query_route import QueryRoute
from functional.utils.helpers import data_helper

# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize(
    ('person_id', 'expected_status', 'expected_response'),
    (
        ('01377f6d-9767-48ce-9e37-3c81f8a3c739', HTTPStatus.OK, person_data.PERSON_DETAIL_DATA),
        ('01377f6d-9767-48ce-9e37-incorrect739', HTTPStatus.NOT_FOUND, person_data.PERSON_GET_NOT_FOUND),
    ),
)
async def test_get_person_by_id(
        make_get_request,
        person_id,
        expected_status,
        expected_response,
):
    """Получение детальной информации о персоне."""
    response, status = await make_get_request(f'{EndPoint.PERSON}/{person_id}')

    assert status == expected_status
    assert response == expected_response


async def test_get_person_films(make_get_request):
    """Получение фильмов по персоне."""
    person_id = '01377f6d-9767-48ce-9e37-3c81f8a3c739'
    response, status = await make_get_request(f'{EndPoint.PERSON}/{person_id}/films')

    assert status == HTTPStatus.OK
    assert response == person_data.PERSON_FILMS_DATA


@pytest.mark.parametrize(
    ('query', 'page_size', 'page_number', 'expected_status', 'expected_response'),
    (
        ('jack', 50, 1, HTTPStatus.OK, person_data.PERSON_SEARCH_DATA),
        ('jack', 50, 100, HTTPStatus.NOT_FOUND, person_data.PERSON_SEARCH_NOT_FOUND),
    ),
)
async def test_search_persons_by_query(
        make_get_request,
        query,
        page_size,
        page_number,
        expected_status,
        expected_response,
):
    """Поиск персон по имени."""
    params = {
        'query': query,
        'page_size': page_size,
        'page_number': page_number,
    }
    response, status = await make_get_request(EndPoint.PERSON_SEARCH, params=params)

    assert status == expected_status
    assert response == expected_response


async def test_search_persons_cache(make_get_request, redis_client):
    """Проверка получения персон по имени из кэша."""
    params = {
        'query': 'marina',
        'page_size': 50,
        'page_number': 1,
    }

    query_parameters = (
        QueryRoute.PERSON_LIST,
        params['query'],
        params['page_size'],
        params['page_number'],
    )
    redis_key = data_helper.generate_redis_key(*query_parameters)

    await make_get_request(EndPoint.PERSON_SEARCH, params=params)
    cache_value = await redis_client.get(redis_key)

    cache_value = json.loads(cache_value)
    assert cache_value[0]['id'] == person_data.PERSON_SEARCH_FROM_CACHE[0]['id']
    assert cache_value[0]['name'] == person_data.PERSON_SEARCH_FROM_CACHE[0]['name']


async def test_get_person_cache(make_get_request, redis_client):
    """Проверка получения персоны по id из кэша."""
    person_id = '035c4793-4864-45b8-8d4f-b86b454c60b0'

    await make_get_request(f'{EndPoint.PERSON}/{person_id}')
    cache_value = await redis_client.get(person_id)

    cache_value = json.loads(cache_value)
    assert cache_value['id'] == person_data.PERSON_GET_FROM_CACHE['id']
    assert cache_value['name'] == person_data.PERSON_GET_FROM_CACHE['name']
