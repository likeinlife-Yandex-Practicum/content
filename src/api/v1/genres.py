from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from models.dto import GenreDetailResponse, GenreShortResponse
from services.genre_service import GenreService, get_genre_service

router = APIRouter()


@router.get(
    '/',
    response_model=list[GenreShortResponse],
    summary='Список жанров',
    description='Список жанров',
    response_description='Список жанров с id, именем',
    tags=['Жанры'],
)
async def genre_search(genre_service: GenreService = Depends(get_genre_service)) -> list[GenreShortResponse]:

    _genre_list = await genre_service.get_by_query()

    if not _genre_list:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genre not found')

    return [GenreShortResponse(
        id=genre.id,
        name=genre.name,
    ) for genre in _genre_list]


@router.get(
    '/{genre_id}',
    response_model=GenreDetailResponse,
    summary='Детальная информация о жанре',
    description='Получение детальной информации о жанре',
    response_description='Детальная информация о жанре',
    tags=['Жанры'],
)
async def genre_details(
        genre_id: str,
        genre_service: GenreService = Depends(get_genre_service),
) -> GenreDetailResponse:

    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genre not found')

    return GenreDetailResponse(
        id=genre.id,
        name=genre.name,
        description=genre.description,
    )
