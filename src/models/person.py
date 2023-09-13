from models.shared.orjson_base_model import OrjsonBaseModel


class Person(OrjsonBaseModel):
    id: str
    name: str
