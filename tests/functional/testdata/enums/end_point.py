from aenum import StrEnum


class EndPoint(StrEnum):
    FILMS = '/api/v1/films'
    FILM_SEARCH = '/api/v1/films/search'
    GENRES = '/api/v1/genres'
    PERSON = '/api/v1/persons'
    PERSON_SEARCH = '/api/v1/persons/search'
