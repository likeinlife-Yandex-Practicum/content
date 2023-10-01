from aenum import StrEnum


class EsIndex(StrEnum):
    """Названия индексов в ElasticSearch."""

    MOVIE = 'movie'
    GENRE = 'genre'
    PERSON = 'person'
