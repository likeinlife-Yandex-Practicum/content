from fastapi import APIRouter, status
from pydantic import BaseModel

router = APIRouter()


class HealthCheck(BaseModel):
    """Response model to validate and return when performing a health check."""

    status: str = 'OK'


@router.get(
    '/health',
    tags=['healthcheck'],
    summary='Проверка состояния сервиса',
    response_description='Состояние сервиса',
    status_code=status.HTTP_200_OK,
    response_model=HealthCheck,
)
def get_health() -> HealthCheck:
    """
    Проверка состояния сервиса.

    Returns:
        HealthCheck: Состояние сервиса
    """
    return HealthCheck(status='OK')
