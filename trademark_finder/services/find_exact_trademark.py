from logging import Logger
from typing import Optional

from pydantic import BaseModel

from trademark_finder.models.trademark import Trademark
from trademark_finder.repositories.trademark import TrademarkRepository


class FindExactTrademarkRequest(BaseModel):
    title: str


class FindExactTrademarkResponse(BaseModel):
    success: bool
    trademark: Optional[Trademark]

    def is_success(self) -> bool:
        return self.success

    @classmethod
    def success_response(cls, trademark: Trademark) -> 'FindExactTrademarkResponse':
        return cls(success=True, trademark=trademark)

    @classmethod
    def error_response(cls) -> 'FindExactTrademarkResponse':
        return cls(success=False)


class FindExactTrademarkService:
    def __init__(
            self,
            trademark_repository: TrademarkRepository,
            logger: Logger,
    ):
        self._trademark_repository = trademark_repository
        self._logger = logger

    def find_exact_trademark(self, request: FindExactTrademarkRequest) -> FindExactTrademarkResponse:
        try:
            trademark = await self._trademark_repository.find_exact(title=request.title)
        except Exception as db_error:
            self._logger.error('Database error: %s', db_error)
            return FindExactTrademarkResponse.error_response()

        return FindExactTrademarkResponse.success_response(trademark)
