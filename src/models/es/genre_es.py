from models.shared.orjson_base_model import OrjsonBaseModel


class GenreEs(OrjsonBaseModel):
    id: str
    genre: str
    description: str | None
