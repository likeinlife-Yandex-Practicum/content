from models.shared.orjson_base_model import OrjsonBaseModel


class Genre(OrjsonBaseModel):
    id: str
    genre: str
    description: str | None
