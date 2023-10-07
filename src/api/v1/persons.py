from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Path

from models.dto import PersonDetailResponse, PersonFilmsResponse
from services.person_service import PersonService, get_person_service

from .paginator import Paginator

router = APIRouter()


@router.get(
    '/search',
    response_model=list[PersonDetailResponse],
    summary='Поиск персон по имени',
    description='Список персон с пагинацией',
    response_description='Список персон с id, именем и фильмами',
    tags=['Персоны'],
)
async def person_search(
        query: Annotated[
            str,
            Query(
                title='запрос',
                description='Поисковое значение'
            )
        ],
        paginator: Paginator = Depends(),
        person_service: PersonService = Depends(get_person_service),
) -> list[PersonDetailResponse]:
    _person_list = await person_service.get_by_query(
        query,
        paginator.page_size,
        paginator.page_number,
    )
    if not _person_list:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='persons not found')

    return [PersonDetailResponse(
        id=person.id,
        name=person.name,
        films=person.movies,
    ) for person in _person_list]


@router.get(
    '/{person_id}',
    response_model=PersonDetailResponse,
    summary='Детальная информация о персоне',
    description='Получение детальной информации о персоне',
    response_description='Детальная информация о персоне',
    tags=['Персоны'],
)
async def person_details(
        person_id: Annotated[
            str,
            Query(
                title='идентификатор персоны',
                description='Идентификатор персоны',
            )
        ],
        person_service: PersonService = Depends(get_person_service),
) -> PersonDetailResponse:
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='person not found')

    return PersonDetailResponse(
        id=person.id,
        name=person.name,
        films=person.movies,
    )


@router.get(
    '/{person_id}/films',
    response_model=list[PersonFilmsResponse],
    summary='Информация о фильмах с участием персоны',
    description='Получение информации о фильмах с персоной',
    response_description='Информация о фильмах с участием персоны',
    tags=['Персоны'],
)
async def person_movies(
        person_id: Annotated[
            str,
            Path(
                title='идентификатор персоны',
                description='Идентификатор персоны',
            )
        ],
        person_service: PersonService = Depends(get_person_service),
) -> list[PersonFilmsResponse]:
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='person not found')

    return [
        PersonFilmsResponse(
            id=movie.id,
            title=movie.title,
            imdb_rating=movie.imdb_rating,
            roles=movie.roles,
        ) for movie in person.movies
    ]
