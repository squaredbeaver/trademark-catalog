from typing import Optional, Any

from aiohttp import web
from pydantic import BaseModel, validator, ValidationError

from trademark_finder.composition_root import CompositionContainer
from trademark_finder.models.trademark import Trademark
from trademark_finder.services.find_similar_trademark import FindSimilarTrademarkServiceRequest


class FindSimilarTrademarkHandlerRequest(BaseModel):
    title: str

    @validator('title')
    def non_empty_title(cls, value: str) -> str:
        if not value:
            raise ValueError('title should not be empty')
        return value


class FindSimilarTrademarkResponse(BaseModel):
    http_code: int
    trademarks: list[Trademark]

    @classmethod
    def success_response(cls, trademarks: list[Trademark]) -> 'FindSimilarTrademarkResponse':
        return cls(http_code=web.HTTPOk.status_code, trademarks=trademarks)

    @classmethod
    def bad_request_response(cls) -> 'FindSimilarTrademarkResponse':
        return cls(http_code=web.HTTPBadRequest.status_code, trademarks=[])

    @classmethod
    def internal_error_response(cls) -> 'FindSimilarTrademarkResponse':
        return cls(http_code=web.HTTPInternalServerError.status_code, trademarks=[])

    def as_web_response(self) -> web.Response:
        response_data = {
            'trademarks': [self._format_trademark(tm) for tm in self.trademarks]
        }
        return web.json_response(response_data, status=self.http_code)

    def _format_trademark(self, trademark: Trademark) -> dict[str, Any]:
        return {
            'id': trademark.id,
            'title': trademark.title,
            'application_number': trademark.application_number,
            'registration_date': trademark.registration_date.isoformat(),
            'expiry_date': trademark.expiry_date.isoformat(),
        }


class FindSimilarTrademarkHandler(web.View):
    def __init__(self, request: web.Request) -> None:
        super().__init__(request)
        composition_container: CompositionContainer = self.request.config_dict['composition_container']
        self._find_similar_tm_service = composition_container.find_similar_trademark_service
        self._logger = composition_container.logger

    async def get(self) -> web.Response:
        request = await self._fetch_request()
        if not request:
            return FindSimilarTrademarkResponse.bad_request_response().as_web_response()

        service_request = FindSimilarTrademarkServiceRequest(title=request.title)
        service_response = await self._find_similar_tm_service.find_similar_trademark(request=service_request)

        if not service_response.is_success():
            return FindSimilarTrademarkResponse.internal_error_response().as_web_response()

        response = FindSimilarTrademarkResponse.success_response(
            trademarks=service_response.trademarks,
        )
        return response.as_web_response()

    async def _fetch_request(self) -> Optional[FindSimilarTrademarkHandlerRequest]:
        try:
            return FindSimilarTrademarkHandlerRequest(
                title=self.request.query.get('title'),
            )
        except (ValidationError, TypeError):
            return None
