import pytest
from pydantic import parse_obj_as

from models.dto import PersonDetailResponse
from models.dto.person_response import PersonFilmsResponse
from tests.constants import BASE_URL

ENDPOINT = f'{BASE_URL}/api/v1/persons'


@pytest.mark.parametrize(
    ('person_id', 'expected_films_len'),
    (
        (
            '979996d5-ef97-427d-a0f5-d640cd1813a4',
            7,
        ),
        (
            'e86eb86b-4115-4dbb-b499-3086e849f36b',
            2,
        ),
    ),
)
def test_get_persons_by_id(client, person_id: str, expected_films_len: int):
    """Тестирование вывода персоны по id."""
    response = client.get(f'{ENDPOINT}/{person_id}')

    assert response.status_code == 200
    result: PersonDetailResponse = parse_obj_as(PersonDetailResponse, response.json())
    assert len(result.films) == expected_films_len


@pytest.mark.parametrize(
    ('query', 'page_size', 'page_number', 'expected_status_code'),
    (
        (
            'jake',
            50,
            1,
            200,
        ),
        (
            'jake',
            50,
            2,
            404,
        ),
        (
            'wood',
            3,
            1,
            200,
        ),
    ),
)
def test_get_persons_by_query(
    client,
    query: str,
    page_size: int,
    page_number: int,
    expected_status_code: int,
):
    """Тестирование вывода персоны по имени."""
    payload = {
        'query': query,
        'page_size': page_size,
        'page_number': page_number,
    }
    response = client.get(f'{ENDPOINT}/search', params=payload)

    assert response.status_code == expected_status_code
    if expected_status_code == 200:
        parse_obj_as(list[PersonDetailResponse], response.json())


@pytest.mark.parametrize(
    ('person_id', 'film_count'),
    (
        (
            '38f10d93-d48c-4d33-ae69-cc8ab20f99e4',
            1,
        ),
        (
            '979996d5-ef97-427d-a0f5-d640cd1813a4',
            7,
        ),
    ),
)
def test_get_person_films_by_person_id(
    client,
    person_id: str,
    film_count: int,
):
    """Тестирование вывода фильмов с участием персоны."""
    response = client.get(f'{ENDPOINT}/{person_id}/films')

    assert response.status_code == 200
    films: list[PersonFilmsResponse] = parse_obj_as(list[PersonFilmsResponse], response.json())

    assert len(films) == film_count
