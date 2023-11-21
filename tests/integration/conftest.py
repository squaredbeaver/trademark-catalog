from datetime import date
from typing import AsyncGenerator

import pytest
from aiohttp import web
from aiohttp.test_utils import BaseTestServer, TestServer, TestClient

from app.application import create_application
from app.configuration import AppConfig


@pytest.fixture(scope='session')
def test_db_admin_user() -> str:
    return 'postgres'


@pytest.fixture(scope='session')
def test_db_admin_password() -> str:
    return 'postgres'


@pytest.fixture(scope='session')
def test_db_user() -> str:
    return 'trademark-catalog-test'


@pytest.fixture(scope='session')
def test_db_password() -> str:
    return 'trademark-catalog-test'


@pytest.fixture(scope='session')
def test_db_name() -> str:
    return 'trademark-catalog-test'


@pytest.fixture
def app_config(postgres_dsn: str):
    return AppConfig(
        postgres_dsn=postgres_dsn,
    )


@pytest.fixture
async def application(
        app_config: AppConfig,
        db: None,
) -> web.Application:
    return await create_application(app_config)


@pytest.fixture
async def app_server(application: web.Application) -> AsyncGenerator[BaseTestServer, None]:
    async with TestServer(application) as server:
        yield server


@pytest.fixture
async def app_client(app_server: TestServer) -> AsyncGenerator[TestClient, None]:
    async with TestClient(app_server) as client:
        yield client


@pytest.fixture
def sample_trademark_data() -> dict[str,]:
    sample_date = date.today().isoformat()
    return {
        'title': 'titlea',
        'description': 'desc',
        'application_number': 'appnum',
        'application_date': sample_date,
        'registration_date': sample_date,
        'expiry_date': sample_date,
    }
