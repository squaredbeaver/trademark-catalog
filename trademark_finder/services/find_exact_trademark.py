from logging import Logger
from typing import Optional

from pydantic import BaseModel

from trademark_finder.models.trademark import Trademark
from trademark_finder.repositories.trademark import TrademarkRepository


class FindExactTrademarkServiceRequest(BaseModel):
    title: str


class FindExactTrademarkServiceResponse(BaseModel):
    success: bool
    trademark: Optional[Trademark]

    def is_success(self) -> bool:
        return self.success

    @classmethod
    def success_response(cls, trademark: Optional[Trademark]) -> 'FindExactTrademarkServiceResponse':
        return cls(success=True, trademark=trademark)

    @classmethod
    def error_response(cls) -> 'FindExactTrademarkServiceResponse':
        return cls(success=False)


class FindExactTrademarkService:
    def __init__(
            self,
            trademark_repository: TrademarkRepository,
            logger: Logger,
    ):
        self._trademark_repository = trademark_repository
        self._logger = logger

    async def find_exact_trademark(self, request: FindExactTrademarkServiceRequest) -> FindExactTrademarkServiceResponse:
        try:
            trademark = await self._trademark_repository.find_exact(title=request.title)
        except Exception as db_error:
            self._logger.error('Database error: %s', db_error)
            return FindExactTrademarkServiceResponse.error_response()

        return FindExactTrademarkServiceResponse.success_response(trademark)
