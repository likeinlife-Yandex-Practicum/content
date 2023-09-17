import uuid

from models.shared.orjson_base_model import OrjsonBaseModel


class GenreEs(OrjsonBaseModel):
    id: uuid.UUID
    genre: str
    description: str | None = None
    movies: list[dict] = []
