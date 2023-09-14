from models.shared.orjson_base_model import OrjsonBaseModel


class FilmEs(OrjsonBaseModel):
    id: str
    title: str
    description: str
