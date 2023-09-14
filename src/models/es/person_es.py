from models.shared.orjson_base_model import OrjsonBaseModel


class PersonEs(OrjsonBaseModel):
    id: str
    name: str
