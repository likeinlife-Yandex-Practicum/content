import uuid

from pydantic import BaseModel

from models.dto.genre_response import GenreShortResponse
from models.dto.person_response import PersonShortResponse


class FilmShortResponse(BaseModel):
    """Краткая информация о фильме."""

    id: uuid.UUID
    title: str
    imdb_rating: float


class FilmDetailResponse(BaseModel):
    """Детальная информация о фильме."""

    id: uuid.UUID
    title: str
    imdb_rating: float
    description: str
    genre: list[GenreShortResponse]
    actors: list[PersonShortResponse]
    writers: list[PersonShortResponse]
    directors: list[PersonShortResponse]
