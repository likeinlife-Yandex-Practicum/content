# Запуск/остановка
- make up - запуск
- make down - стоп

## Альтернативный метод запуска/остановки
- docker compose up -d
- docker compose down

# Адрес api
http://localhost:8000

## Адрес для проверки удачного запуска
http://localhost:8000/api/openapi

# Переменные окружения
Смотреть .test.env

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
    id: string,
    imdb_rating: float,
    genre: [string],
    title: string,
    description: string,
    director: [string],
    actors_names: [string],
    writers_names: [string],
    actors: [
        {
            id: string,
            name: string
        }
    ],
    writers: [
        {
            id: string,
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
    id: string,
    name: string,
    description: string,
    movies: [
        {
            id: string,
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
    id: string,
    name: string,
    movies: [
        {
            id: string,
            title: string,
            role: string
        }
    ]
}
```
</details>
