from aenum import StrEnum


class EsIndex(StrEnum):
    """Названия индексов в ElasticSearch."""

    MOVIES = 'movies'
    GENRE = 'genre'
    PERSON = 'person'
