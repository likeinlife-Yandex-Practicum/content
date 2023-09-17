import uuid

from models.shared.orjson_base_model import OrjsonBaseModel


class PersonEs(OrjsonBaseModel):
    id: uuid.UUID
    name: str
    movies: list[dict] = []
