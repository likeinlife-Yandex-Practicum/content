import uuid

from models.shared.orjson_base_model import OrjsonBaseModel


class PersonFilm(OrjsonBaseModel):
    id: uuid.UUID
    title: str
    imdb_rating: float
    roles: list[str]


class PersonEs(OrjsonBaseModel):
    id: uuid.UUID
    name: str
    movies: list[PersonFilm]
