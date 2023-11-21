from typing import Any

import pytest
from aiohttp.test_utils import TestClient


@pytest.fixture
async def sample_trademark(
        app_client: TestClient,
        sample_trademark_data: dict[str, Any],
):
    await app_client.post('/trademark', json=sample_trademark_data)


async def test_search_exact_success(
        app_client: TestClient,
        sample_trademark_data: dict[str, Any],
        sample_trademark: None,
):
    response = await app_client.get(f'/trademark?title={sample_trademark_data['title']}')
    assert response.status == 200

    response_body = await response.json()
    assert response_body['result'][0]['title'] == sample_trademark_data['title']


async def test_search_similar_success(
        app_client: TestClient,
        sample_trademark_data: dict[str, Any],
        sample_trademark: None,
):
    response = await app_client.get(f'/trademark?title=titleb&exact_match=false')
    assert response.status == 200

    response_body = await response.json()
    assert response_body['result'][0]['title'] == sample_trademark_data['title']
