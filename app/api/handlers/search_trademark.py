from typing import Annotated

from aiohttp import web
from pydantic import BaseModel, Field, StringConstraints, ValidationError

from app.api.base_response import BaseResponse
from app.api.codes import HttpCode
from app.composition_root import CompositionContainer
from app.models.trademark import Trademark
from app.services.search_trademark import SearchTrademarkService, SearchTrademarkServiceRequest


class SearchTrademarkHandlerRequest(BaseModel):
    title: Annotated[str, StringConstraints(min_length=1)]
    exact_match: bool = True


class SearchTrademarkHandlerResponse(BaseResponse):
    http_code: HttpCode
    result: list[Trademark] = Field(default_factory=list)

    @classmethod
    def ok_response(cls, result: list[Trademark]) -> 'SearchTrademarkHandlerResponse':
        return cls(http_code=HttpCode.ok, result=result)


async def search_trademark(request: web.Request) -> web.Response:
    composition_container: CompositionContainer = request.config_dict['composition_container']
    search_tm_service: SearchTrademarkService = composition_container.search_tm_service

    try:
        handler_request = SearchTrademarkHandlerRequest.model_validate(request.query)
    except ValidationError:
        return SearchTrademarkHandlerResponse.bad_request_response().as_web_response()

    service_request = SearchTrademarkServiceRequest.model_validate(handler_request.model_dump())
    service_response = await search_tm_service.invoke(request=service_request)

    if service_response.is_success():
        if not service_response.result:
            return SearchTrademarkHandlerResponse.not_found_response().as_web_response()

        return SearchTrademarkHandlerResponse.ok_response(result=service_response.result).as_web_response()

    return SearchTrademarkHandlerResponse.internal_error_response().as_web_response()
