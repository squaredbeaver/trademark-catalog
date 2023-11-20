import logging
from datetime import date
from unittest.mock import AsyncMock

import pytest

from app.models.trademark import Trademark


@pytest.fixture(scope='session')
def logger() -> logging.Logger:
    logger = logging.getLogger()
    logger.level = logging.DEBUG
    logger.propagate = False
    handler = logging.StreamHandler()
    logging_format = '%(asctime)s %(levelname)s %(message)s'
    formatter = logging.Formatter(fmt=logging_format)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


@pytest.fixture
def trademark_repository() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def sample_trademark() -> Trademark:
    return Trademark(
        title='abc',
        description='desc',
        application_number='appnum',
        application_date=date.today(),
        registration_date=date.today(),
        expiry_date=date.today(),
    )
