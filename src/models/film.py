from models.shared.orjson_base_model import OrjsonBaseModel


class Film(OrjsonBaseModel):
    id: str
    title: str
    description: str
