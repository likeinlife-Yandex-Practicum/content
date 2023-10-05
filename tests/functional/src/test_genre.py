import json
from http import HTTPStatus

import pytest
from functional.testdata import genre_data
from functional.testdata.enums.end_point import EndPoint


@pytest.mark.asyncio
@pytest.mark.parametrize(
    (
        'genre_id',
        'expected_status',
        'expected_response',
    ),
    (
        (
            '0b105f87-e0a5-45dc-8ce7-f8632088f390',
            HTTPStatus.OK,
            genre_data.GENRE_DETAIL_DATA,
        ),
        (
            '0b105f87-e0a5-45dc-8ce7-f8632088f391',
            HTTPStatus.NOT_FOUND,
            genre_data.GENRE_NOT_FOUND,
        ),
    ),
)
async def test_get_genre_by_id(
    make_get_request,
    genre_id,
    expected_status,
    expected_response,
):
    """Получение детальной информации о жанре."""
    response, status = await make_get_request(f'{EndPoint.GENRES}/{genre_id}')

    assert status == expected_status
    assert response == expected_response


@pytest.mark.asyncio
async def test_get_genre_by_id_from_cache(
    make_get_request,
    redis_client,
):
    """Получение жанра из кэша."""
    genre_id = '0b105f87-e0a5-45dc-8ce7-f8632088f390'
    await make_get_request(f'{EndPoint.GENRES}/{genre_id}')
    cache_value = await redis_client.get(genre_id)

    cache_value = json.loads(cache_value)
    assert cache_value['id'] == genre_data.GENRE_DETAIL_DATA['id']
    assert cache_value['name'] == genre_data.GENRE_DETAIL_DATA['name']
    assert cache_value['description'] == genre_data.GENRE_DETAIL_DATA['description']


@pytest.mark.asyncio
async def test_get_genres(make_get_request):
    """Получение списка жанров."""
    expected_status = HTTPStatus.OK
    response, status = await make_get_request(f'{EndPoint.GENRES}')

    assert status == expected_status
    assert response == genre_data.GENRE_LIST_DATA
