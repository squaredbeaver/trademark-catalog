from datetime import date
from logging import Logger
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.trademark import Trademark
from app.repositories.trademark import TrademarkRepository
from app.services.register_trademark import RegisterTrademarkService, RegisterTrademarkServiceRequest


@pytest.fixture
def register_tm_request() -> RegisterTrademarkServiceRequest:
    return RegisterTrademarkServiceRequest(
        title='abc',
        description='desc',
        application_number='appnum',
        application_date=date.today(),
        registration_date=date.today(),
        expiry_date=date.today(),
    )


@pytest.fixture
def register_tm_service(logger: Logger, trademark_repository: TrademarkRepository) -> RegisterTrademarkService:
    return RegisterTrademarkService(
        logger=logger,
        db_session_factory=MagicMock(),
        trademark_repository=trademark_repository,
    )


async def test_register_success(
        trademark_repository: AsyncMock,
        register_tm_service: RegisterTrademarkService,
        register_tm_request: RegisterTrademarkServiceRequest,
) -> None:
    trademark_repository.find_exact = AsyncMock(return_value=None)
    trademark_repository.create = AsyncMock()
    response = await register_tm_service.invoke(register_tm_request)
    assert response.is_success()


async def test_register_already_registered(
        trademark_repository: AsyncMock,
        register_tm_service: RegisterTrademarkService,
        register_tm_request: RegisterTrademarkServiceRequest,
        sample_trademark: Trademark,
) -> None:
    trademark_repository.find_exact = AsyncMock(return_value=sample_trademark)
    response = await register_tm_service.invoke(register_tm_request)
    assert response.is_already_registered()


async def test_register_error(
        trademark_repository: AsyncMock,
        register_tm_service: RegisterTrademarkService,
        register_tm_request: RegisterTrademarkServiceRequest,
) -> None:
    trademark_repository.find_exact = AsyncMock(side_effect=Exception)
    response = await register_tm_service.invoke(register_tm_request)
    assert response.is_error()
