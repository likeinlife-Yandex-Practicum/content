import json

import pytest
import http

from functional.testdata.enums import EndPoint
from functional.testdata.enums.query_route import QueryRoute
from functional.testdata.film_data import FILM_LIST_BY_TITLE_GOT_FROM_CACHE, FILM_LIST_BY_TITLE_PUT_TO_CACHE
from functional.utils.helpers import data_helper

# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio


async def test_search_with_by_title(make_get_request):
    """Поиск фильма по части названия."""
    payload = {'query': 'The Star'}
    expected_answer = {'status': http.HTTPStatus.OK, 'length': 50}

    body, status = await make_get_request(EndPoint.FILM_SEARCH, params=payload)

    assert status == expected_answer['status']
    assert len(body) == expected_answer['length']


async def test_search_film_by_title_empty_result(make_get_request):
    """Поиск фильма по части названия. Пустой результат поиска."""
    payload = {'query': 'asdlkjsaopfj222as'}
    expected_status = http.HTTPStatus.NOT_FOUND
    expected_body = {'detail': 'films not found'}

    body, status = await make_get_request(EndPoint.FILM_SEARCH, params=payload)

    assert status == expected_status
    assert body == expected_body


async def test_search_film_by_title_with_page_size(make_get_request):
    """Поиск фильма по части названия указанием числа результатов на странице."""
    payload = {
        'query': 'Star',
        'page_size': 8,
    }
    expected_status = http.HTTPStatus.OK
    expected_length = 8

    body, status = await make_get_request(EndPoint.FILM_SEARCH, params=payload)

    assert status == expected_status
    assert len(body) == expected_length


async def test_search_film_by_title_with_page_number(make_get_request):
    """Поиск фильма по части названия указанием номера страницы."""
    payload = {
        'query': 'Star',
        'page_size': 8,
        'page_number': 2,
    }
    expected_status = http.HTTPStatus.OK
    expected_length = 8

    body, status = await make_get_request(EndPoint.FILM_SEARCH, params=payload)

    assert status == expected_status
    assert len(body) == expected_length


async def test_search_film_by_all_params_is_put_to_cache(redis_client, make_get_request):
    """Проверка сохранения данных в кэш Redis по набору параметров."""
    payload = {
        'query': 'Star',
        'page_size': 1,
        'page_number': 1,
    }

    query_parameters = (
        QueryRoute.FILM_LIST,
        None,
        payload['query'],
        None,
        payload['page_size'],
        payload['page_number']
    )
    redis_key = data_helper.generate_redis_key(*query_parameters)
    film_data = FILM_LIST_BY_TITLE_GOT_FROM_CACHE

    await make_get_request(EndPoint.FILM_SEARCH, params=payload)
    cache_value = await redis_client.get(redis_key)
    cache_film_data = json.loads(cache_value)

    assert len(cache_film_data) == 1
    assert cache_film_data[0]['id'] == film_data[0]['id']
    assert cache_film_data[0]['title'] == film_data[0]['title']
    assert cache_film_data[0]['imdb_rating'] == film_data[0]['imdb_rating']
    assert cache_film_data[0]['description'] == film_data[0]['description']
    assert cache_film_data[0]['genre'] == film_data[0]['genre']
    assert cache_film_data[0]['directors'] == film_data[0]['directors']
    assert cache_film_data[0]['actors'] == film_data[0]['actors']
    assert cache_film_data[0]['writers'] == film_data[0]['writers']


async def test_search_film_by_all_params_is_got_from_cache(redis_client, make_get_request):
    """Проверка получения данных из кэша Redis по набору параметров."""
    payload = {
        'query': 'Make php',
        'page_size': 1,
        'page_number': 1,
    }

    query_parameters = (
        QueryRoute.FILM_LIST,
        None,
        payload['query'],
        None,
        payload['page_size'],
        payload['page_number']
    )
    redis_key = data_helper.generate_redis_key(*query_parameters)
    film_data = FILM_LIST_BY_TITLE_PUT_TO_CACHE
    expected_status = http.HTTPStatus.OK

    await redis_client.set(redis_key, json.dumps(film_data))

    await make_get_request(EndPoint.FILMS, params=payload)
    body, status = await make_get_request(EndPoint.FILM_SEARCH, params=payload)

    assert status == expected_status
    assert len(body) == 1
    assert body[0]['id'] == film_data[0]['id']
    assert body[0]['title'] == film_data[0]['title']
    assert body[0]['imdb_rating'] == film_data[0]['imdb_rating']
