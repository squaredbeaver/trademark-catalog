import os
from importlib import util

import pytest
from psycopg2 import connect
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from yarl import URL
from yoyo import get_backend, read_migrations


@pytest.fixture(scope='session')
def random_db_name() -> str:
    random_suffix = os.urandom(4).hex()
    return f'pytest-{random_suffix}'


@pytest.fixture(scope='session')
def test_db_admin_user() -> str:
    return os.getenv('TEST_DB_ADMIN_USER', 'postgres')


@pytest.fixture(scope='session')
def test_db_admin_password() -> str:
    return os.getenv('TEST_DB_ADMIN_PASSWORD', 'postgres')


@pytest.fixture(scope='session')
def test_db_user() -> str:
    return os.getenv('TEST_DB_USER', 'postgres-test')


@pytest.fixture(scope='session')
def test_db_password() -> str:
    return os.getenv('TEST_DB_PASSWORD', 'postgres-test')


@pytest.fixture(scope='session')
def test_db_host() -> str:
    return os.getenv('TEST_DB_HOST', 'localhost')


@pytest.fixture(scope='session')
def test_db_port() -> int:
    return int(os.getenv('TEST_DB_PORT', 5432))


@pytest.fixture(scope='session')
def test_db_name(random_db_name: str) -> str:
    return os.getenv('TEST_DB_NAME', random_db_name)


def drop_create_db(
        postgres_superuser_dsn: str,
        test_db_user: str,
        test_db_name: str,
        test_db_password: str,
) -> None:
    """Создать чистую тестовую БД."""
    connection = connect(postgres_superuser_dsn)
    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = connection.cursor()
    cursor.execute(f'DROP DATABASE IF EXISTS "{test_db_name}"')
    cursor.execute(f'DROP USER IF EXISTS "{test_db_user}"')
    cursor.execute(f'CREATE DATABASE "{test_db_name}"')
    cursor.execute(f'CREATE USER "{test_db_user}" WITH ENCRYPTED PASSWORD \'{test_db_password}\'')
    cursor.execute(f'GRANT ALL PRIVILEGES ON DATABASE "{test_db_name}" to "{test_db_user}"')
    connection.close()


def apply_migrations(postgres_dsn: str, migrations_module: str = 'migrations.sql') -> None:
    """Применить миграции БД."""
    migrations_location = util.find_spec(migrations_module)
    migrations = read_migrations(migrations_location.submodule_search_locations[0])

    backend = get_backend(postgres_dsn)
    with backend.lock():
        backend.apply_migrations(backend.to_apply(migrations))


def wipe_db_schema(postgres_dsn: str, schema: str = 'data') -> None:
    """Очистить схему БД."""
    conn = connect(postgres_dsn)
    cur = conn.cursor()

    query_tables = f"""
    SELECT table_name
    FROM "information_schema"."tables"
    WHERE table_schema = '{schema}'
    """

    cur.execute(query_tables)
    table_names = [row[0] for row in cur.fetchall()]

    if table_names:
        wipe_tables = '\n'.join(
            f'DELETE FROM "{schema}"."{table}";'
            for table in table_names
        )
        cur.execute(wipe_tables)
        conn.commit()

    conn.close()


@pytest.fixture(scope='session')
def postgres_dsn(
        test_db_user: str,
        test_db_password: str,
        test_db_host: str,
        test_db_port: int,
        test_db_name: str,
) -> str:
    url = URL.build(
        scheme='postgresql',
        user=test_db_user,
        password=test_db_password,
        host=test_db_host,
        port=test_db_port,
        path=f'/{test_db_name}',
    )
    return str(url)


@pytest.fixture(scope='session')
def postgres_superuser_dsn(
        test_db_admin_user: str,
        test_db_admin_password: str,
        test_db_host: str,
        test_db_port: int,
        test_db_name: str,
) -> str:
    url = URL.build(
        scheme='postgresql',
        user=test_db_admin_user,
        password=test_db_admin_password,
        host=test_db_host,
        port=test_db_port,
    )
    return str(url)


@pytest.fixture(scope='session')
def clean_db(
        postgres_dsn: str,
        postgres_superuser_dsn: str,
        test_db_user: str,
        test_db_name: str,
        test_db_password: str,
) -> None:
    """Фикстура чистой БД.

    Вызывается один раз за сессию. Необходима для того, чтобы чистая база с миграциями
    создавалась только один раз для фикстуры db.
    """
    drop_create_db(postgres_superuser_dsn, test_db_user, test_db_name, test_db_password)
    apply_migrations(postgres_dsn)


@pytest.fixture(scope='function')
def db(clean_db: None, postgres_dsn: str) -> None:
    """Фикстура базы данных.

    Переиспользует созданную на старте сессии БД, очищая схему data перед каждым тестом.
    """
    wipe_db_schema(postgres_dsn, schema='data')
