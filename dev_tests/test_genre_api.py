import pytest
from pydantic import parse_obj_as

from models.dto import GenreShortResponse

from .constants import BASE_URL

ENDPOINT = f'{BASE_URL}/api/v1/genres'


def test_get_genre_search(client):
    """Тестирование вывода списка жанров."""
    response = client.get(f'{ENDPOINT}')

    assert response.status_code == 200
    result = parse_obj_as(list[GenreShortResponse], response.json())
    assert len(result) == 26


@pytest.mark.parametrize(
    ('genre_id', 'genre_name'),
    (
        (
            '3d8d9bf5-0d90-4353-88ba-4ccc5d2c07ff',
            'Action',
        ),
        (
            '6c162475-c7ed-4461-9184-001ef3d9f26e',
            'Sci-Fi',
        ),
    ),
)
def test_get_genre_by_id(client, genre_id: str, genre_name: str):
    """Тестирование вывода жанра по id."""
    response = client.get(f'{ENDPOINT}/{genre_id}')

    assert response.status_code == 200
    result: GenreShortResponse = parse_obj_as(GenreShortResponse, response.json())
    assert result.name == genre_name
