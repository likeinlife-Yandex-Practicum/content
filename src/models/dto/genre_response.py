from pydantic import BaseModel


class GenreResponse(BaseModel):
    id: str
    genre: str
