import json

import pytest
import http

from functional.testdata.enums import EndPoint
from functional.testdata.enums.query_route import QueryRoute
from functional.testdata.film_data import (DETAILED_FILM_DATA, DETAILED_FILM_DATA_PUT_TO_CACHE,
                                           FILM_LIST_BY_GENRE_GOT_FROM_CACHE, FILM_LIST_BY_GENRE_PUT_TO_CACHE,
                                           DETAILED_FILM_DATA_GOT_FROM_CACHE)
from functional.utils.helpers import data_helper

# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio


async def test_get_film_by_id(make_get_request):
    """Получение детальной информации о фильме."""
    film_id = 'cddf9b8f-27f9-4fe9-97cb-9e27d4fe3394'
    expected_status = http.HTTPStatus.OK

    body, status = await make_get_request(f'{EndPoint.FILMS}/{film_id}')

    assert status == expected_status
    assert body == DETAILED_FILM_DATA


async def test_film_by_id_is_put_to_cache(redis_client, make_get_request):
    """Проверка сохранения данных в кэш Redis по id фильма."""
    film_id = 'c20959d2-daca-4cb2-a104-e1ab63479da3'
    film_data = DETAILED_FILM_DATA_GOT_FROM_CACHE

    await make_get_request(f'{EndPoint.FILMS}/{film_id}')
    cache_value = await redis_client.get(film_id)

    assert json.loads(cache_value) == film_data, 'No film in cache'


async def test_film_by_id_is_got_from_cache(redis_client, make_get_request):
    """Проверка получения данных из кэша Redis по id фильма."""
    expected_status = http.HTTPStatus.OK
    film_data = DETAILED_FILM_DATA_PUT_TO_CACHE

    await redis_client.set(film_data['id'], json.dumps(film_data))
    body, status = await make_get_request(f'{EndPoint.FILMS}/{film_data["id"]}')

    assert status == expected_status
    assert body == film_data


async def test_get_film_by_id_empty_result(make_get_request):
    """Получение детальной информации о фильме. Пустой результат поиска."""
    film_id = 'be823372-d799-4a87-a53c-bff76bb24c7b'
    expected_status = http.HTTPStatus.NOT_FOUND
    expected_body = {'detail': 'film not found'}

    body, status = await make_get_request(f'{EndPoint.FILMS}/{film_id}')

    assert status == expected_status
    assert body == expected_body


async def test_filter_by_genre_param(make_get_request):
    """Фильтрация списка фильмов по жанру."""
    payload = {
        'genre': '9c91a5b2-eb70-4889-8581-ebe427370edd',
    }
    expected_status = http.HTTPStatus.OK
    expected_length = 24

    body, status = await make_get_request(EndPoint.FILMS, params=payload)

    assert status == expected_status
    assert all(body[i]['imdb_rating'] >= body[i + 1]['imdb_rating'] for i in range(len(body) - 1)), 'Not sorted by DESC'
    assert len(body) == expected_length


async def test_filter_by_genre_param_empty_result(make_get_request):
    """Фильтрация списка фильмов по жанру. Пустой результат поиска."""
    payload = {
        'genre': 'f920f5ed-00ea-4431-ad87-e6be07af27be',
    }
    expected_status = http.HTTPStatus.NOT_FOUND
    expected_body = {'detail': 'films not found'}

    body, status = await make_get_request(EndPoint.FILMS, params=payload)

    assert status == expected_status
    assert body == expected_body


async def test_filter_by_genre_param_with_sorting_desc(make_get_request):
    """Фильтрации списка фильмов по жанру с сортировкой по рейтингу DESC."""
    payload = {
        'genre': '9c91a5b2-eb70-4889-8581-ebe427370edd',
        'sort': '-imdb_rating',
    }
    expected_status = http.HTTPStatus.OK
    expected_length = 24

    body, status = await make_get_request(EndPoint.FILMS, params=payload)

    assert status == expected_status
    assert all(body[i]['imdb_rating'] >= body[i + 1]['imdb_rating'] for i in range(len(body) - 1)), 'Not sorted by DESC'
    assert len(body) == expected_length


async def test_filter_by_genre_param_with_sorting_asc(make_get_request):
    """Фильтрация списка фильмов по жанру с сортировкой по рейтингу ASC."""
    payload = {
        'genre': '9c91a5b2-eb70-4889-8581-ebe427370edd',
        'sort': 'imdb_rating',
    }
    expected_status = http.HTTPStatus.OK
    expected_length = 24

    body, status = await make_get_request(EndPoint.FILMS, params=payload)

    assert status == expected_status
    assert all(body[i]['imdb_rating'] <= body[i + 1]['imdb_rating'] for i in range(len(body) - 1)), 'Not sorted by ASC'
    assert len(body) == expected_length


async def test_filter_by_genre_param_with_page_size(make_get_request):
    """Фильтрация списка фильмов по жанру с указанием числа результатов на странице."""
    payload = {
        'genre': '9c91a5b2-eb70-4889-8581-ebe427370edd',
        'page_size': 5,
    }
    expected_status = http.HTTPStatus.OK
    expected_length = 5

    body, status = await make_get_request(EndPoint.FILMS, params=payload)

    assert status == expected_status
    assert len(body) == expected_length


async def test_filter_by_genre_param_with_page_number(make_get_request):
    """Фильтрация списка фильмов по жанру с указанием номера страницы."""
    payload = {
        'genre': '9c91a5b2-eb70-4889-8581-ebe427370edd',
        'page_size': 10,
        'page_number': 3,
    }
    expected_status = http.HTTPStatus.OK
    expected_length = 4

    body, status = await make_get_request(EndPoint.FILMS, params=payload)

    assert status == expected_status
    assert len(body) == expected_length


async def test_filter_by_genre_param_with_all_params(make_get_request):
    """Фильтрации списка фильмов по жанру с всеми параметрами."""
    payload = {
        'genre': '9c91a5b2-eb70-4889-8581-ebe427370edd',
        'sort': 'imdb_rating',
        'page_size': 15,
        'page_number': 1,
    }
    expected_status = http.HTTPStatus.OK
    expected_length = 15

    body, status = await make_get_request(EndPoint.FILMS, params=payload)

    assert status == expected_status
    assert all(body[i]['imdb_rating'] <= body[i + 1]['imdb_rating'] for i in range(len(body) - 1)), 'Not sorted by ASC'
    assert len(body) == expected_length


@pytest.mark.parametrize('sort_value', [
    '+imdb_rating',
    'imdb_rating-'
    '-imdb_rating100500',
    'genre',
])
async def test_filter_by_genre_sort_param_validation(make_get_request, sort_value):
    """Валидация параметра sort."""
    payload = {
        'genre': '9c91a5b2-eb70-4889-8581-ebe427370edd',
        'sort': sort_value,
    }
    expected_status = http.HTTPStatus.UNPROCESSABLE_ENTITY
    expected_body = {
        'detail': [{
            'ctx': {
                'pattern': '^-?imdb_rating$'
            },
            'loc': ['query', 'sort'],
            'msg': 'string does not match regex "^-?imdb_rating$"',
            'type': 'value_error.str.regex'
        }]
    }

    body, status = await make_get_request(EndPoint.FILMS, params=payload)

    assert status == expected_status
    assert body == expected_body


async def test_filter_by_genre_param_with_all_params_is_put_cache(redis_client, make_get_request):
    """Проверка сохранения данных в кэш Redis по набору параметров."""
    payload = {
        'genre': '9c91a5b2-eb70-4889-8581-ebe427370edd',
        'sort': 'imdb_rating',
        'page_size': 1,
        'page_number': 1,
    }
    query_parameters = (
        QueryRoute.FILM_LIST,
        payload['genre'],
        None,
        payload['sort'],
        payload['page_size'],
        payload['page_number']
    )
    redis_key = data_helper.generate_redis_key(*query_parameters)
    film_data = FILM_LIST_BY_GENRE_GOT_FROM_CACHE

    await make_get_request(EndPoint.FILMS, params=payload)
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


async def test_filter_by_genre_param_with_all_params_got_from_cache(redis_client, make_get_request):
    """Проверка получения данных из кэша Redis по набору параметров."""
    payload = {
        'genre': '9c91a5b2-eb70-4889-8581-ebe427370edd',
        'sort': 'imdb_rating',
        'page_size': 1,
        'page_number': 1,
    }
    query_parameters = (
        QueryRoute.FILM_LIST,
        payload['genre'],
        None,
        payload['sort'],
        payload['page_size'],
        payload['page_number']
    )
    redis_key = data_helper.generate_redis_key(*query_parameters)
    expected_status = http.HTTPStatus.OK
    film_data = FILM_LIST_BY_GENRE_PUT_TO_CACHE

    await redis_client.set(redis_key, json.dumps(film_data))

    await make_get_request(EndPoint.FILMS, params=payload)
    body, status = await make_get_request(EndPoint.FILMS, params=payload)

    assert status == expected_status
    assert len(body) == 1
    assert body[0]['id'] == film_data[0]['id']
    assert body[0]['title'] == film_data[0]['title']
    assert body[0]['imdb_rating'] == film_data[0]['imdb_rating']
