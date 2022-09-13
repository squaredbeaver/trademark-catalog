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
