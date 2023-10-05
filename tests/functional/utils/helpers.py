import hashlib
import json
from pathlib import Path
from typing import Any

from elasticsearch import AsyncElasticsearch, helpers
from faker import Faker

from functional.testdata.enums.es_index import EsIndex


class DataHelper:
    """Вспомогательный класс для работы с тестовыми данными."""

    def __init__(self):
        self.faker = Faker()

    @staticmethod
    async def get_json_file_data(*relative_path: str) -> dict:
        base_dir = Path(__file__).parent.parent / 'testdata'
        absolute_path = base_dir.joinpath(*relative_path)
        with open(absolute_path, 'r') as f:
            data = json.load(f)
            return data

    async def create_test_data(self, es_client: AsyncElasticsearch):
        movie_data = await self.get_json_file_data('movie.data.json')
        await helpers.async_bulk(client=es_client, actions=movie_data, index=EsIndex.MOVIE, refresh=True)
        genre_data = await self.get_json_file_data('genre.data.json')
        await helpers.async_bulk(client=es_client, actions=genre_data, index=EsIndex.GENRE, refresh=True)
        person_data = await self.get_json_file_data('person.data.json')
        await helpers.async_bulk(client=es_client, actions=person_data, index=EsIndex.PERSON, refresh=True)

    @staticmethod
    def generate_redis_key(*args: Any) -> str:
        """Генерация md5-хеша из значений переданных аргументов."""
        return hashlib.md5(str(args).encode('utf-8')).hexdigest()


data_helper = DataHelper()
