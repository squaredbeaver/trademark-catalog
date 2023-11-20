from enum import IntEnum
from logging import Logger
from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints

from app.models.trademark import Trademark
from app.repositories.database_session import DatabaseSessionFactory
from app.repositories.trademark import TrademarkRepository


class SearchTrademarkServiceRequest(BaseModel):
    title: Annotated[str, StringConstraints(min_length=1)]
    exact_match: bool = True
    similarity: float = Field(gt=0, lt=1, default=0.5)


class SearchTrademarkServiceResponseCode(IntEnum):
    success = 0
    error = 1


class SearchTrademarkServiceResponse(BaseModel):
    code: SearchTrademarkServiceResponseCode
    result: list[Trademark] = Field()

    def is_success(self) -> bool:
        return self.code is SearchTrademarkServiceResponseCode.success

    def is_error(self) -> bool:
        return self.code is SearchTrademarkServiceResponseCode.error

    @classmethod
    def success_response(cls, result: list[Trademark]) -> 'SearchTrademarkServiceResponse':
        return cls(code=SearchTrademarkServiceResponseCode.success, result=result)

    @classmethod
    def error_response(cls) -> 'SearchTrademarkServiceResponse':
        return cls(code=SearchTrademarkServiceResponseCode.error, result=[])


class SearchTrademarkService:
    def __init__(
            self,
            logger: Logger,
            db_session_factory: DatabaseSessionFactory,
            trademark_repository: TrademarkRepository,
    ):
        self._logger = logger
        self._db_session_factory = db_session_factory
        self._trademark_repository = trademark_repository

    async def invoke(
            self,
            request: SearchTrademarkServiceRequest,
    ) -> SearchTrademarkServiceResponse:
        if request.exact_match:
            return await self._find_exact(title=request.title)

        return await self._find_similar(title=request.title, similarity=request.similarity)

    async def _find_exact(self, title: str) -> SearchTrademarkServiceResponse:
        try:
            async with self._db_session_factory.create_session() as db_session:
                trademark = await self._trademark_repository.find_exact(title=title, session=db_session)
        except Exception as db_error:
            self._logger.error('Database error: %s', db_error)
            return SearchTrademarkServiceResponse.error_response()

        result = []
        if trademark is not None:
            result.append(trademark)

        return SearchTrademarkServiceResponse.success_response(result=result)

    async def _find_similar(self, title: str, similarity: float) -> SearchTrademarkServiceResponse:
        try:
            async with self._db_session_factory.create_session() as db_session:
                trademarks = await self._trademark_repository.find_similar(
                    title=title,
                    similarity=similarity,
                    session=db_session,
                )
        except Exception as db_error:
            self._logger.error('Database error: %s', db_error)
            return SearchTrademarkServiceResponse.error_response()

        return SearchTrademarkServiceResponse.success_response(result=trademarks)
