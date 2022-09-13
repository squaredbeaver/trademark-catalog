from typing import Optional

from asyncpg import Connection

from trademark_finder.models.trademark import Trademark
from trademark_finder.repositories.base import BaseRepository


class TrademarkRepository(BaseRepository):
    table_name = 'data.trademark'
    fields = (
        'id',
        'title',
        'description',
        'application_number',
        'application_date',
        'registration_date',
        'expiry_date',
    )

    async def create(self, trademark: Trademark, *, ext_connection: Optional[Connection] = None) -> None:
        async with self.ensure_connection(ext_connection) as connection:
            await self._create(trademark, connection)

    async def create_many(self, trademarks: list[Trademark], *, ext_connection: Optional[Connection] = None) -> None:
        async with self.ensure_connection(ext_connection) as connection:
            await self._create_many(trademarks, connection)

    async def find_exact(self, title: str, *, ext_connection: Optional[Connection] = None) -> Optional[Trademark]:
        async with self.ensure_connection(ext_connection) as connection:
            return await self._find_exact(title, connection)

    async def find_similar(
            self,
            title: str,
            similarity: float,
            *,
            ext_connection: Optional[Connection] = None,
    ) -> list[Trademark]:
        async with self.ensure_connection(ext_connection) as connection:
            return await self._find_similar(title, similarity, connection)

    async def _create(self, trademark: Trademark, connection: Connection) -> None:
        positions = self._get_positions()
        query_args = self._get_query_args(source=trademark)

        sql = f"""
        INSERT INTO {self.table_name} ({self.columns})
        VALUES ({positions})
        """

        await connection.execute(sql, *query_args)

    async def _create_many(self, trademarks: list[Trademark], connection: Connection) -> None:
        positions = self._get_positions()
        query_args = [self._get_query_args(source=trademark) for trademark in trademarks]

        sql = f"""
        INSERT INTO {self.table_name} ({self.columns})
        VALUES ({positions})
        """

        await connection.executemany(sql, query_args)

    async def _find_exact(
        self,
        title: str,
        connection: Connection,
    ) -> Optional[Trademark]:
        sql = f"""
        SELECT *
        FROM {self.table_name}
        WHERE title = $1
        """

        record = await connection.fetchrow(sql, title)
        if not record:
            return None

        return Trademark(**record)

    async def _find_similar(
        self,
        title: str,
        similarity: float,
        connection: Connection,
    ) -> list[Trademark]:
        sql = f"""
        SELECT *
        FROM {self.table_name}
        WHERE title % $1 AND similarity(title, $1) > $2
        """

        records = await connection.fetch(sql, title, similarity)
        return [Trademark(**record) for record in records]
