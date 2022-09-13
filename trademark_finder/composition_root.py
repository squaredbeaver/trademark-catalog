from logging import Logger
from typing import NamedTuple

from asyncpg import Pool

from trademark_finder.repositories.trademark import TrademarkRepository
from trademark_finder.services.find_exact_trademark import FindExactTrademarkService
from trademark_finder.services.find_similar_trademark import FindSimilarTrademarkService


class CompositionContainer(NamedTuple):
    logger: Logger

    connection_pool: Pool

    trademark_repository: TrademarkRepository

    find_exact_trademark_service: FindExactTrademarkService
    find_similar_trademark_service: FindSimilarTrademarkService
