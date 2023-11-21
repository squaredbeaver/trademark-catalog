import logging
import sys
from contextlib import AsyncExitStack

from aiohttp import web
from asyncpg import create_pool, Pool

from app.api.urls import urls
from app.composition_root import CompositionContainer
from app.configuration import AppConfig
from app.repositories.database_session import DatabaseSessionFactory
from app.repositories.trademark import TrademarkRepository
from app.services.register_trademark import RegisterTrademarkService
from app.services.search_trademark import SearchTrademarkService


async def create_application(config: AppConfig) -> web.Application:
    exit_stack = AsyncExitStack()

    async def _cleanup(app: web.Application) -> None:  # noqa: WPS430
        await exit_stack.aclose()

    logging.basicConfig(stream=sys.stdout, level='NOTSET')
    logger = logging.getLogger()
    logger.setLevel(config.logging_level)

    db_connection_pool: Pool = await create_pool(
        dsn=str(config.postgres_dsn),
        min_size=0,
        max_size=10,
    )
    exit_stack.push_async_callback(db_connection_pool.close)

    db_session_factory = DatabaseSessionFactory(
        connection_pool=db_connection_pool,
    )

    trademark_repository = TrademarkRepository()

    search_tm_service = SearchTrademarkService(
        logger=logger,
        db_session_factory=db_session_factory,
        trademark_repository=trademark_repository,
    )
    register_tm_service = RegisterTrademarkService(
        logger=logger,
        db_session_factory=db_session_factory,
        trademark_repository=trademark_repository,
    )

    composition_container = CompositionContainer(
        logger=logger,
        connection_pool=db_connection_pool,
        trademark_repository=trademark_repository,
        search_tm_service=search_tm_service,
        register_tm_service=register_tm_service,
    )

    application = web.Application()
    application['composition_container'] = composition_container
    application.add_routes(urls)
    application.on_cleanup.append(_cleanup)

    return application
