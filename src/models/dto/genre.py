from pydantic import BaseModel


class Genre(BaseModel):
    id: str
    genre: str
