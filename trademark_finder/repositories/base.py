from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from functools import cached_property
from logging import Logger
from typing import Any, Optional

from asyncpg import Connection, Pool
from pydantic import BaseModel


class BaseRepository(ABC):
    def __init__(self, connection_pool: Pool, logger: Logger) -> None:
        self.connection_pool = connection_pool
        self.logger = logger

    @property
    @abstractmethod
    def table_name(self) -> str:
        pass

    @property
    @abstractmethod
    def fields(self) -> tuple[str, ...]:
        pass

    @cached_property
    def columns(self) -> str:
        return ', '.join(self.fields)

    @asynccontextmanager
    async def ensure_connection(self, ext_connection: Optional[Connection] = None) -> Connection:
        if ext_connection:
            yield ext_connection
        else:
            async with self.connection_pool.acquire() as connection:
                async with connection.transaction():
                    yield connection

    def _get_positions(
            self,
            *,
            start: int = 1,
    ) -> str:
        if start < 1:
            raise ValueError('start must be greater than 0')

        end = start + len(self.fields)
        return ', '.join(f'${pos}' for pos in range(start, end))

    def _get_query_args(
            self,
            source: BaseModel,
            *,
            start: int = 0,
    ) -> list[Any]:
        return [getattr(source, field) for field in self.fields[start:]]
