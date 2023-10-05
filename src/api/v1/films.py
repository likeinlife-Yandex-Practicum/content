from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from models.dto import FilmShortResponse
from models.dto.film_response import FilmDetailResponse
from services.film_service import FilmService, get_film_service

from .paginator import Paginator

router = APIRouter()


@router.get(
    '/search',
    response_model=list[FilmShortResponse],
    summary='Поиск фильмов по названию',
    description='Список фильмов с пагинацией',
    response_description='Список фильмов с id, названием и рейтингом',
    tags=['Фильмы'],
)
async def film_search(
        query: str,
        paginator: Paginator = Depends(),
        film_service: FilmService = Depends(get_film_service),
) -> list[FilmShortResponse]:
    _film_list = await film_service.get_by_query(
        None,
        query,
        None,
        paginator.page_size,
        paginator.page_number,
    )
    if not _film_list:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='films not found')

    return [FilmShortResponse(
        id=film.id,
        title=film.title,
        imdb_rating=film.imdb_rating,
    ) for film in _film_list]


@router.get(
    '/{film_id}',
    response_model=FilmDetailResponse,
    summary='Детальная информация о фильме',
    description='Получение детальной информации о фильме',
    response_description='Детальная информация о фильме',
    tags=['Фильмы'],
)
async def film_details(
        film_id: str,
        film_service: FilmService = Depends(get_film_service),
) -> FilmDetailResponse:
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')

    return FilmDetailResponse(
        id=film.id,
        title=film.title,
        imdb_rating=film.imdb_rating,
        description=film.description,
        genre=film.genre,
        actors=film.actors,
        writers=film.writers,
        directors=film.directors,
    )


@router.get(
    '/',
    response_model=list[FilmShortResponse],
    summary='Список фильмов',
    description='Список фильмов с пагинацией, фильтрацией по жанрам и сортировкой рейтингу',
    response_description='Список фильмов с id, названием и рейтингом',
    tags=['Фильмы'],
)
async def film_list(
        genre: str | None = None,
        paginator: Paginator = Depends(),
        sort: Annotated[str | None, Query(regex='^-?imdb_rating$')] = '-imdb_rating',
        film_service: FilmService = Depends(get_film_service),
) -> list[FilmShortResponse]:
    _film_list = await film_service.get_by_query(
        genre,
        None,
        sort,
        paginator.page_size,
        paginator.page_number,
    )
    if not _film_list:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='films not found')

    return [FilmShortResponse(
        id=film.id,
        title=film.title,
        imdb_rating=film.imdb_rating,
    ) for film in _film_list]
