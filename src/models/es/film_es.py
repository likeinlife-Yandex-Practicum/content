import uuid

from models.shared.orjson_base_model import OrjsonBaseModel


class FilmEs(OrjsonBaseModel):
    id: uuid.UUID
    title: str
    imdb_rating: float
    description: str | None = None
    genre: list[dict] = []
    directors: list[dict] = []
    actors: list[dict] = []
    writers: list[dict] = []
