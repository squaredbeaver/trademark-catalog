from logging import Logger
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.trademark import Trademark
from app.repositories.trademark import TrademarkRepository
from app.services.search_trademark import SearchTrademarkService, SearchTrademarkServiceRequest


@pytest.fixture
def search_tm_service(logger: Logger, trademark_repository: TrademarkRepository) -> SearchTrademarkService:
    return SearchTrademarkService(
        logger=logger,
        db_session_factory=MagicMock(),
        trademark_repository=trademark_repository,
    )


async def test_find_exact_success(
        trademark_repository: AsyncMock,
        search_tm_service: SearchTrademarkService,
        sample_trademark: Trademark,
) -> None:
    trademark_repository.find_exact = AsyncMock(return_value=sample_trademark)

    request = SearchTrademarkServiceRequest(title='abc', exact_match=True)
    response = await search_tm_service.invoke(request)

    assert response.is_success()


async def test_find_similar_success(
        trademark_repository: AsyncMock,
        search_tm_service: SearchTrademarkService,
        sample_trademark: Trademark,
) -> None:
    trademark_repository.find_similar = AsyncMock(return_value=[sample_trademark])

    request = SearchTrademarkServiceRequest(title='abc', exact_match=False)
    response = await search_tm_service.invoke(request)

    assert response.is_success()


async def test_error(
        trademark_repository: AsyncMock,
        search_tm_service: SearchTrademarkService,
) -> None:
    trademark_repository.find_exact = AsyncMock(side_effect=Exception)
    trademark_repository.find_similar = AsyncMock(side_effect=Exception)

    request = SearchTrademarkServiceRequest(title='abc', exact_match=True)
    response = await search_tm_service.invoke(request)
    assert response.is_error()

    request = SearchTrademarkServiceRequest(title='abc', exact_match=False)
    response = await search_tm_service.invoke(request)
    assert response.is_error()
