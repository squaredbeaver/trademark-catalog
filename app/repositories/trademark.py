from app.models.trademark import Trademark
from app.repositories.base_repository import BaseRepository
from app.repositories.database_session import DatabaseSession


class TrademarkRepository(BaseRepository):
    table_name = 'data.trademark'
    fields = tuple(Trademark.model_fields.keys())

    async def create(self, trademark: Trademark, session: DatabaseSession) -> None:
        positions = self._get_positions()
        query_args = self._get_query_args(source=trademark)

        sql = f"""
        INSERT INTO {self.table_name} ({self.columns})
        VALUES ({positions})
        """

        await session.execute(sql, *query_args)

    async def find_exact(self, title: str, session: DatabaseSession) -> Trademark | None:
        sql = f"""
        SELECT *
        FROM {self.table_name}
        WHERE title = $1
        """

        rows = await session.fetch(sql, title)
        if not rows:
            return None

        return Trademark(**rows[0])

    async def find_similar(self, title: str, similarity: float, session: DatabaseSession) -> list[Trademark]:
        sql = f"""
        SELECT *
        FROM {self.table_name}
        WHERE title % $1 AND similarity(title, $1) > $2
        """

        rows = await session.fetch(sql, title, similarity)
        return [Trademark(**record) for record in rows]
