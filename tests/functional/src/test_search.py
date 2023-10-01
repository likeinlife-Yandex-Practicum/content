import pytest

from functional.testdata.enums import EndPoint


@pytest.mark.parametrize('query_data, expected_answer', [
    ({'query': 'The Star'}, {'status': 200, 'length': 50}),
    ({'query': 'qwertyasdasd'}, {'status': 404, 'length': 1}),  # todo: у нас детали, а непустой список
])
@pytest.mark.asyncio
async def test_search(make_get_request, query_data, expected_answer):
    body, status = await make_get_request(EndPoint.FILM_SEARCH, params=query_data)

    assert status == expected_answer['status']
    assert len(body) == expected_answer['length']
