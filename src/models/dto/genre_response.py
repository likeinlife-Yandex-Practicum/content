import uuid

from pydantic import BaseModel


class GenreShortResponse(BaseModel):
    """Краткая информация о жанре."""

    id: uuid.UUID
    name: str


class GenreDetailResponse(BaseModel):
    """Детальная информация о жанре."""

    id: uuid.UUID
    name: str
    description: str
