import logging
from typing import Any, Sequence

from asyncpg import Connection


class DBClient:
    def __init__(self, connection: Connection) -> None:
        self._logger = logging.getLogger('db_client')
        self._connection = connection

    async def insert(self, table_name: str, record: dict[str, Any]) -> None:
        columns, values = zip(*record.items())
        sql = f"""
        INSERT INTO {table_name} ({', '.join(columns)})
        VALUES ({self._get_insert_positions(values)})
        """  # noqa: WPS237
        await self._connection.execute(sql, *values)

    async def select(self, table_name: str, **filters: Any) -> list[Any]:
        where_clause, filter_values = self._get_where_condition(**filters)
        sql = f"""
        SELECT *
        FROM {table_name}
        {where_clause}
        """

        return await self._connection.fetch(sql, *filter_values)

    def _get_where_condition(self, **filters: Any) -> tuple[str, list[Any]]:
        where_clause = ''
        filter_values = []

        if filters:
            where_clause = f'WHERE {self._get_select_positions(**filters)}'
            filter_values = list(filters.values())

        return where_clause, filter_values

    def _get_select_positions(self, **where_constraints: Any) -> str:
        return ' AND '.join(
            f'{sql_field} = ${field_n}'
            for field_n, sql_field in enumerate(where_constraints, start=1)
        )

    def _get_insert_positions(self, fields: Sequence[str]) -> str:
        return ', '.join(
            f'${field_n}'
            for field_n in range(1, len(fields) + 1)
        )
