from logging import Logger
from typing import NamedTuple

from asyncpg import Pool

from app.repositories.trademark import TrademarkRepository
from app.services.register_trademark import RegisterTrademarkService
from app.services.search_trademark import SearchTrademarkService


class CompositionContainer(NamedTuple):
    logger: Logger
    connection_pool: Pool

    trademark_repository: TrademarkRepository

    register_tm_service: RegisterTrademarkService
    search_tm_service: SearchTrademarkService
