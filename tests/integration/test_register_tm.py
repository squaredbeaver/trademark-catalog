from typing import Any

from aiohttp.test_utils import TestClient


async def test_register_success(
        app_client: TestClient,
        sample_trademark_data: dict[str, Any],
):
    response = await app_client.post('/trademark', json=sample_trademark_data)
    assert response.status == 201

    title = sample_trademark_data['title']
    response = await app_client.get(f'/trademark?title={title}')
    assert response.status == 200

    response_body = await response.json()
    assert response_body['result'][0]['title'] == title
