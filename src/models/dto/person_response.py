import uuid

from pydantic import BaseModel


class PersonShortResponse(BaseModel):
    """Краткая информация о человеке."""

    id: uuid.UUID
    name: str


class PersonFilmsModel(BaseModel):
    """Фильмы, в которых человек принимал участие."""

    id: uuid.UUID
    title: str
    roles: list[str]


class PersonFilmsResponse(BaseModel):
    """Фильмы, в которых человек принимал участие."""

    id: uuid.UUID
    title: str
    imdb_rating: float
    roles: list[str]


class PersonDetailResponse(BaseModel):
    """Детальная информация о человеке."""

    id: uuid.UUID
    name: str
    films: list[PersonFilmsModel]
