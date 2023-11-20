from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Optional

from asyncpg import Connection, Pool


class DatabaseSession:
    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    async def execute(self, query: str, *args: Any) -> None:
        await self._connection.execute(query, *args)

    async def fetch(self, query: str, *args: Any) -> Any:
        return await self._connection.fetch(query, *args)


class DatabaseSessionFactory:
    def __init__(
            self,
            connection_pool: Pool,
            acquire_timeout: Optional[int] = None,
    ) -> None:
        self._connection_pool = connection_pool
        self._acquire_timeout = acquire_timeout

    @asynccontextmanager
    async def create_session(self) -> AsyncGenerator[DatabaseSession, None]:
        async with self._connection_pool.acquire(timeout=self._acquire_timeout) as connection:
            yield DatabaseSession(connection=connection)
