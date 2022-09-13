import logging
import sys
from contextlib import AsyncExitStack

from aiohttp import web
from asyncpg import create_pool, Pool

from trademark_finder.composition_root import CompositionContainer
from trademark_finder.configuration import AppConfig
from trademark_finder.repositories.trademark import TrademarkRepository
from trademark_finder.services.find_exact_trademark import FindExactTrademarkService
from trademark_finder.services.find_similar_trademark import FindSimilarTrademarkService
from trademark_finder.urls import urls


def setup_logger(config: AppConfig) -> logging.Logger:
    logging.basicConfig(stream=sys.stdout, level='NOTSET')
    logger = logging.getLogger('trademark-finder')
    logger.setLevel(config.logging_level)
    return logger


async def create_dependencies(
        config: AppConfig,
        exit_stack: AsyncExitStack,
) -> CompositionContainer:
    logger = setup_logger(config)
    db_connection_pool: Pool = await create_pool(config.postgres_dsn)
    exit_stack.push_async_callback(db_connection_pool.close)

    trademark_repository = TrademarkRepository(
        connection_pool=db_connection_pool,
        logger=logger,
    )

    find_exact_tm_service = FindExactTrademarkService(
        trademark_repository=trademark_repository,
        logger=logger,
    )
    find_similar_tm_service = FindSimilarTrademarkService(
        trademark_repository=trademark_repository,
        logger=logger,
    )

    return CompositionContainer(
        logger=logger,
        connection_pool=db_connection_pool,
        trademark_repository=trademark_repository,
        find_exact_trademark_service=find_exact_tm_service,
        find_similar_trademark_service=find_similar_tm_service,
    )


async def create_app(config: AppConfig) -> web.Application:
    exit_stack = AsyncExitStack()
    composition_container = await create_dependencies(config, exit_stack)

    async def _cleanup(app: web.Application) -> None:
        await exit_stack.aclose()

    application = web.Application()
    application['composition_container'] = composition_container
    application.add_routes(urls)
    application.on_cleanup.append(_cleanup)

    return application
