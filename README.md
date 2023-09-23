# Async API Sprint 1

## Авторы
* Anton Vysotskiy [@likeinlife](https://github.com/likeinlife)
* Maxim Zaitsev [@maxim-zaitsev](https://github.com/maxim-zaitsev)

# Установка
- git clone https://github.com/likeinlife/Async_API_sprint_1.git
- Скопировать файл ./.env.example в файл ./.env
- Заполнить .env своими данными
- через Makefile выполнить команды:
  - make up
  - make fill (потребуется несколько минут для загрузки дамп в ElasticSearch)

# Запуск/остановка
- make up - запуск
- make fill - заполнить данными elasticsearch
- make down - удалить созданные контейнеры
- make downv - удалить созданные контейнеры, включая volumes

# Тестирование
- pip install pytest requests
- pytest -v -l ./tests

# Адрес api
http://localhost:80

## Адрес для проверки удачного запуска
http://localhost:80/api/openapi

# Переменные окружения
Смотреть .env.example

# Дампы elastic
ETL-процесс сделан в другом репозитории, т.к. это независимые сервисы.
https://github.com/likeinlife/YA-ETL
Дампы сделаны с помощью инструмента elasticsearch-dump:
https://github.com/elasticsearch-dump/elasticsearch-dump

# Структура индексов
<details>
<summary>movie</summary>

```
{
    id: uuid,
    imdb_rating: float,
    genre: {
        id: uuid,
        name: str
    },
    title: string,
    description: string,
    directors: [
        {
            id: uuid,
            name: string
        }
    ],
    actors: [
        {
            id: uuid,
            name: string
        }
    ],
    writers: [
        {
            id: uuid,
            name: string
        }
    ]
}
```
</details>

<details>
<summary>genre</summary>

```
{
    id: uuid,
    name: string,
    description: string,
    movies: [
        {
            id: uuid,
            title: string,
            imdb_rating: float
        }
    ]
}
```
</details>

<details>
<summary>person</summary>

```
{
    id: uuid,
    name: string,
    movies: [
        {
            id: uuid,
            title: string,
            imdb_rating: float,
            roles: [string]
        }
    ]
}
```
</details>
