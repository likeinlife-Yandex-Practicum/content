from aenum import StrEnum


class EndPoint(StrEnum):
    FILMS = '/api/v1/films'
    FILM_SEARCH = '/api/v1/films/search'
