from fastapi import Query
from pydantic import BaseModel, Field


class Paginator(BaseModel):
    page_size: int = Field(
        Query(
            default=50,
            title='размер страницы',
            description='Количество записей на странице',
            ge=1,
            le=250
        )
    )

    page_number: int = Field(
        Query(
            default=1,
            title='номер страницы',
            description='Порядковый номер страницы',
            ge=1)
    )
