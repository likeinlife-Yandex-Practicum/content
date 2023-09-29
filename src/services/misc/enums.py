from aenum import StrEnum, auto


class QueryRoute(StrEnum):
    FILM_LIST = auto()
    GENRE_LIST = auto()
    PERSON_LIST = auto()
