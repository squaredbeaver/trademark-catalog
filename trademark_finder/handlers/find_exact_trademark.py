from typing import Optional, Any

from aiohttp import web
from pydantic import BaseModel, validator, ValidationError

from trademark_finder.composition_root import CompositionContainer
from trademark_finder.models.trademark import Trademark
from trademark_finder.services.find_exact_trademark import FindExactTrademarkServiceRequest


class FindExactTrademarkHandlerRequest(BaseModel):
    title: str

    @validator('title')
    def non_empty_title(cls, value: str) -> str:
        if not value:
            raise ValueError('title should not be empty')
        return value


class FindExactTrademarkResponse(BaseModel):
    http_code: int
    trademark: Optional[Trademark]

    @classmethod
    def success_response(cls, trademark: Trademark) -> 'FindExactTrademarkResponse':
        return cls(http_code=web.HTTPOk.status_code, trademark=trademark)

    @classmethod
    def not_found_response(cls) -> 'FindExactTrademarkResponse':
        return cls(http_code=web.HTTPNotFound.status_code)

    @classmethod
    def bad_request_response(cls) -> 'FindExactTrademarkResponse':
        return cls(http_code=web.HTTPBadRequest.status_code)

    @classmethod
    def internal_error_response(cls) -> 'FindExactTrademarkResponse':
        return cls(http_code=web.HTTPInternalServerError.status_code)

    def as_web_response(self) -> web.Response:
        response_data = {
            'trademark': self._format_trademark(self.trademark),
        }
        return web.json_response(response_data, status=self.http_code)

    def _format_trademark(self, trademark: Optional[Trademark]) -> Optional[dict[str, Any]]:
        if not trademark:
            return None
        return {
            'id': trademark.id,
            'title': trademark.title,
            'application_number': trademark.application_number,
            'registration_date': trademark.registration_date.isoformat(),
            'expiry_date': trademark.expiry_date.isoformat(),
        }


class FindExactTrademarkHandler(web.View):
    def __init__(self, request: web.Request) -> None:
        super().__init__(request)
        composition_container: CompositionContainer = self.request.config_dict['composition_container']
        self._find_exact_tm_service = composition_container.find_exact_trademark_service
        self._logger = composition_container.logger

    async def get(self) -> web.Response:
        request = await self._fetch_request()
        if not request:
            return FindExactTrademarkResponse.bad_request_response().as_web_response()

        service_request = FindExactTrademarkServiceRequest(title=request.title)
        service_response = await self._find_exact_tm_service.find_exact_trademark(request=service_request)

        if not service_response.is_success():
            return FindExactTrademarkResponse.internal_error_response().as_web_response()

        if not service_response.trademark:
            return FindExactTrademarkResponse.not_found_response().as_web_response()

        response = FindExactTrademarkResponse.success_response(
            trademark=service_response.trademark,
        )
        return response.as_web_response()

    async def _fetch_request(self) -> Optional[FindExactTrademarkHandlerRequest]:
        try:
            return FindExactTrademarkHandlerRequest(
                title=self.request.query.get('title'),
            )
        except (ValidationError, TypeError):
            return None
