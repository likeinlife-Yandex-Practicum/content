from models.base_model import BaseModel


class Genre(BaseModel):
    id: str
    genre: str
    description: str | None
