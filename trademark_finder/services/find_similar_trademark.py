from logging import Logger

from pydantic import BaseModel, Field

from trademark_finder.models.trademark import Trademark
from trademark_finder.repositories.trademark import TrademarkRepository


class FindSimilarTrademarkRequest(BaseModel):
    title: str
    similarity: float = Field(gt=0, lt=1, default=0.5)


class FindSimilarTrademarkResponse(BaseModel):
    success: bool
    trademarks: list[Trademark]

    def is_success(self) -> bool:
        return self.success

    @classmethod
    def success_response(cls, trademarks: list[Trademark]) -> 'FindSimilarTrademarkResponse':
        return cls(success=True, trademarks=trademarks)

    @classmethod
    def error_response(cls) -> 'FindSimilarTrademarkResponse':
        return cls(success=False, trademarks=[])


class FindSimilarTrademarkService:
    def __init__(
            self,
            trademark_repository: TrademarkRepository,
            logger: Logger,
    ):
        self._trademark_repository = trademark_repository
        self._logger = logger

    def find_similar_trademark(self, request: FindSimilarTrademarkRequest) -> FindSimilarTrademarkResponse:
        try:
            trademarks = await self._trademark_repository.find_similar(
                title=request.title,
                similarity=request.similarity,
            )
        except Exception as db_error:
            self._logger.error('Database error: %s', db_error)
            return FindSimilarTrademarkResponse.error_response()

        return FindSimilarTrademarkResponse.success_response(trademarks)
