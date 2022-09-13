from logging import Logger

from pydantic import BaseModel, Field

from trademark_finder.models.trademark import Trademark
from trademark_finder.repositories.trademark import TrademarkRepository


class FindSimilarTrademarkServiceRequest(BaseModel):
    title: str
    similarity: float = Field(gt=0, lt=1, default=0.5)


class FindSimilarTrademarkServiceResponse(BaseModel):
    success: bool
    trademarks: list[Trademark]

    def is_success(self) -> bool:
        return self.success

    @classmethod
    def success_response(cls, trademarks: list[Trademark]) -> 'FindSimilarTrademarkServiceResponse':
        return cls(success=True, trademarks=trademarks)

    @classmethod
    def error_response(cls) -> 'FindSimilarTrademarkServiceResponse':
        return cls(success=False, trademarks=[])


class FindSimilarTrademarkService:
    def __init__(
            self,
            trademark_repository: TrademarkRepository,
            logger: Logger,
    ):
        self._trademark_repository = trademark_repository
        self._logger = logger

    async def find_similar_trademark(
            self,
            request: FindSimilarTrademarkServiceRequest,
    ) -> FindSimilarTrademarkServiceResponse:
        try:
            trademarks = await self._trademark_repository.find_similar(
                title=request.title,
                similarity=request.similarity,
            )
        except Exception as db_error:
            self._logger.error('Database error: %s', db_error)
            return FindSimilarTrademarkServiceResponse.error_response()

        return FindSimilarTrademarkServiceResponse.success_response(trademarks)
