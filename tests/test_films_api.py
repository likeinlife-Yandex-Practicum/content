import pytest
from pydantic import parse_obj_as

from models.dto import FilmShortResponse
from tests.constants import BASE_URL

ENDPOINT = f'{BASE_URL}/api/v1/films'


def test_filter_by_genre_param(client):
    """Тестирование фильтрации списка фильмов по жанру."""
    payload = {
        'genre': '9c91a5b2-eb70-4889-8581-ebe427370edd',
    }
    response = client.get(f'{ENDPOINT}', params=payload)

    assert response.status_code == 200
    result = parse_obj_as(list[FilmShortResponse], response.json())
    assert len(result) == 23


def test_filter_by_genre_param_empty_result(client):
    """Тестирование фильтрации списка фильмов по жанру. Пустой результат поиска."""
    payload = {
        'genre': 'f920f5ed-00ea-4431-ad87-e6be07af27be',
    }
    response = client.get(f'{ENDPOINT}', params=payload)

    assert response.status_code == 404
    result = response.json()
    assert result == {'detail': 'films not found'}


def test_filter_by_genre_param_with_sorting_desc(client):
    """Тестирование фильтрации списка фильмов по жанру с сортировкой по рейтингу DESC."""
    payload = {
        'genre': '9c91a5b2-eb70-4889-8581-ebe427370edd',
        'sort': '-imdb_rating',
    }
    response = client.get(f'{ENDPOINT}', params=payload)

    assert response.status_code == 200
    result = parse_obj_as(list[FilmShortResponse], response.json())
    assert len(result) == 23


def test_filter_by_genre_param_with_sorting_asc(client):
    """Тестирование фильтрации списка фильмов по жанру с сортировкой по рейтингу ASC."""
    payload = {
        'genre': '9c91a5b2-eb70-4889-8581-ebe427370edd',
        'sort': 'imdb_rating',
    }
    response = client.get(f'{ENDPOINT}', params=payload)

    assert response.status_code == 200
    result = parse_obj_as(list[FilmShortResponse], response.json())
    assert len(result) == 23


def test_filter_by_genre_param_with_page_size(client):
    """Тестирование фильтрации списка фильмов по жанру с указанием числа результатов на странице."""
    payload = {
        'genre': '9c91a5b2-eb70-4889-8581-ebe427370edd',
        'page_size': 5,
    }
    response = client.get(f'{ENDPOINT}', params=payload)

    assert response.status_code == 200
    result = parse_obj_as(list[FilmShortResponse], response.json())
    assert len(result) == 5


def test_filter_by_genre_param_with_page_number(client):
    """Тестирование фильтрации списка фильмов по жанру с указанием номера страницы."""
    payload = {
        'genre': '9c91a5b2-eb70-4889-8581-ebe427370edd',
        'page_size': 10,
        'page_number': 3,
    }
    response = client.get(f'{ENDPOINT}', params=payload)

    assert response.status_code == 200
    result = parse_obj_as(list[FilmShortResponse], response.json())
    assert len(result) == 10


def test_filter_by_genre_param_with_all_params(client):
    """Тестирование фильтрации списка фильмов по жанру с всеми параметрами."""
    payload = {
        'genre': '9c91a5b2-eb70-4889-8581-ebe427370edd',
        'sort': 'imdb_rating',
        'page_size': 15,
        'page_number': 1,
    }
    response = client.get(f'{ENDPOINT}', params=payload)

    assert response.status_code == 200
    result = parse_obj_as(list[FilmShortResponse], response.json())
    assert len(result) == 15


@pytest.mark.parametrize('sort_value', [
    '+imdb_rating',
    'imdb_rating-'
    '-imdb_rating100500',
    'genre',
])
def test_filter_by_genre_sort_param_validation(client, sort_value):
    """Валидация параметра sort."""
    payload = {
        'genre': '9c91a5b2-eb70-4889-8581-ebe427370edd',
        'sort': sort_value,
    }
    response = client.get(f'{ENDPOINT}', params=payload)

    assert response.status_code == 422
    result = response.json()
    assert result == {'detail': [{'ctx': {'pattern': '^-?imdb_rating$'}, 'loc': ['query', 'sort'],
                                  'msg': 'string does not match regex "^-?imdb_rating$"',
                                  'type': 'value_error.str.regex'}]}


def test_search_film_by_title(client):
    """Тестирование поиска фильма по части названия."""
    payload = {
        'query': 'Star',
    }
    response = client.get(f'{ENDPOINT}/search', params=payload)

    assert response.status_code == 200
    result = parse_obj_as(list[FilmShortResponse], response.json())
    assert len(result) == 50


def test_search_film_by_title_empty_result(client):
    """Тестирование поиска фильма по части названия. Пустой результат поиска."""
    payload = {
        'query': 'asdlkjsaopfj222as',
    }
    response = client.get(f'{ENDPOINT}/search', params=payload)

    assert response.status_code == 404
    result = response.json()
    assert result == {'detail': 'films not found'}


def test_search_film_by_title_with_page_size(client):
    """Тестирование поиска фильма по части названия указанием числа результатов на странице."""
    payload = {
        'query': 'Star',
        'page_size': 8,
    }
    response = client.get(f'{ENDPOINT}/search', params=payload)

    assert response.status_code == 200
    result = parse_obj_as(list[FilmShortResponse], response.json())
    assert len(result) == 8


def test_search_film_by_title_with_page_number(client):
    """Тестирование поиска фильма по части названия указанием номера страницы."""
    payload = {
        'query': 'Star',
        'page_size': 8,
        'page_number': 2,
    }
    response = client.get(f'{ENDPOINT}/search', params=payload)

    assert response.status_code == 200
    result = parse_obj_as(list[FilmShortResponse], response.json())
    assert len(result) == 8


def test_get_film_by_id(client):
    """Тестирование получения детальной информации о фильме."""
    film_id = 'cddf9b8f-27f9-4fe9-97cb-9e27d4fe3394'
    response = client.get(f'{ENDPOINT}/{film_id}')

    assert response.status_code == 200
    result = response.json()
    assert result == {'id': 'cddf9b8f-27f9-4fe9-97cb-9e27d4fe3394',
                      'title': 'Star Wars: Episode VII - The Force Awakens', 'imdb_rating': 7.9,
                      'description': '30 years after the defeat of Darth Vader and the Empire, Rey, '
                                     'a scavenger from the planet Jakku, finds a BB-8 droid that knows '
                                     'the whereabouts of the long lost Luke Skywalker. Rey, as well as a '
                                     'rogue stormtrooper and two smugglers, are thrown into the middle of a '
                                     'battle between the Resistance and the daunting legions of the First Order.',
                      'genre': [{'id': '120a21cf-9097-479e-904a-13dd7198c1dd', 'name': 'Adventure'},
                                {'id': '3d8d9bf5-0d90-4353-88ba-4ccc5d2c07ff', 'name': 'Action'},
                                {'id': '6c162475-c7ed-4461-9184-001ef3d9f26e', 'name': 'Sci-Fi'}],
                      'actors': [{'id': '26e83050-29ef-4163-a99d-b546cac208f8', 'name': 'Mark Hamill'},
                                 {'id': '2d6f6284-13ce-4d25-9453-c4335432c116', 'name': 'Adam Driver'},
                                 {'id': '5b4bf1bc-3397-4e83-9b17-8b10c6544ed1', 'name': 'Harrison Ford'},
                                 {'id': 'b5d2b63a-ed1f-4e46-8320-cf52a32be358', 'name': 'Carrie Fisher'}],
                      'writers': [{'id': '3217bc91-bcfc-44eb-a609-82d228115c50', 'name': 'Lawrence Kasdan'},
                                  {'id': 'a1758395-9578-41af-88b8-3f9456e6d938', 'name': 'J.J. Abrams'},
                                  {'id': 'a5a8f573-3cee-4ccc-8a2b-91cb9f55250a', 'name': 'George Lucas'},
                                  {'id': 'cec00f0e-200b-4b48-9ed1-2f8fc3c67427', 'name': 'Michael Arndt'}],
                      'directors': [{'id': 'a1758395-9578-41af-88b8-3f9456e6d938', 'name': 'J.J. Abrams'}]}


def test_get_film_by_id_empty_result(client):
    """Тестирование получения детальной информации о фильме. Пустой результат поиска."""
    film_id = 'be823372-d799-4a87-a53c-bff76bb24c7b'
    response = client.get(f'{ENDPOINT}/{film_id}')

    assert response.status_code == 404
    result = response.json()
    assert result == {'detail': 'film not found'}
