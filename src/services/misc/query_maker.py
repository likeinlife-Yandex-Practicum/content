import abc


class BaseQueryMaker(abc.ABC):

    @abc.abstractmethod
    def get_query(self) -> dict | None:
        ...


class FilmQueryMaker(BaseQueryMaker):

    def __init__(self, genre_id: str | None = None, title: str | None = None) -> None:
        self.genre_id = genre_id
        self.title = title

    def get_query(self) -> dict | None:
        query = {'bool': {}}
        if self.title:
            match = {'match': {'title': self.title}}
        else:
            match = {'match_all': {}}

        query['bool'].update({'must': [match]})

        if self.genre_id:
            query['bool'].update({
                'filter': {
                    'nested': {
                        'path': 'genre',
                        'query': {
                            'term': {
                                'genre.id': self.genre_id
                            }
                        }
                    }
                },
            })

        return query


class PersonQueryMaker(BaseQueryMaker):

    def __init__(self, name: str | None = None) -> None:
        self.name = name

    def get_query(self) -> dict | None:
        query = {'bool': {}}
        if self.name:
            match = {'match': {'name': self.name}}
        else:
            match = {'match_all': {}}

        query['bool'].update({'must': [match]})

        return query
