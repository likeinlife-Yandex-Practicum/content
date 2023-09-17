from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from models.dto.film_response import FilmDetailResponse
from services.film_service import FilmService, get_film_service

router = APIRouter()


@router.get('/{film_id}',
            response_model=FilmDetailResponse,
            summary='Детальная информация о фильме',
            description='Получение детальной информации о фильме',
            response_description='Детальная информация о фильме',
            tags=['Фильмы']
            )
async def film_details(film_id: str, film_service: FilmService = Depends(get_film_service)) -> FilmDetailResponse:
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
