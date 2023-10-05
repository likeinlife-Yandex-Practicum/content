from typing import Annotated

from fastapi import Query
from pydantic import BaseModel


class Paginator(BaseModel):
    page_size: Annotated[int, Query(ge=1, le=250)] = 50
    page_number: Annotated[int, Query(ge=1)] = 1
