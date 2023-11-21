from datetime import date
from typing import Annotated

from aiohttp import web
from pydantic import BaseModel, StringConstraints, ValidationError

from app.api.base_response import BaseResponse
from app.api.codes import HttpCode
from app.composition_root import CompositionContainer
from app.models.trademark import Trademark
from app.services.register_trademark import RegisterTrademarkService, RegisterTrademarkServiceRequest


class RegisterTrademarkHandlerRequest(BaseModel):
    title: Annotated[str, StringConstraints(min_length=1)]
    description: str | None
    application_number: str
    application_date: date
    registration_date: date
    expiry_date: date


class RegisterTrademarkHandlerResponse(BaseResponse):
    result: Trademark | None = None

    @classmethod
    def created_response(cls, result: Trademark) -> 'RegisterTrademarkHandlerResponse':
        return cls(http_code=HttpCode.created, result=result)


async def register_trademark(request: web.Request) -> web.Response:
    composition_container: CompositionContainer = request.config_dict['composition_container']
    register_tm_service: RegisterTrademarkService = composition_container.register_tm_service

    request_body = await request.json()
    try:
        handler_request = RegisterTrademarkHandlerRequest.model_validate(request_body)
    except ValidationError:
        return RegisterTrademarkHandlerResponse.bad_request_response().as_web_response()

    service_request = RegisterTrademarkServiceRequest.model_validate(handler_request.model_dump())
    service_response = await register_tm_service.invoke(request=service_request)

    if service_response.is_success() and service_response.result is not None:
        return RegisterTrademarkHandlerResponse.created_response(result=service_response.result).as_web_response()

    if service_response.is_already_registered():
        return RegisterTrademarkHandlerResponse.conflict_response().as_web_response()

    return RegisterTrademarkHandlerResponse.internal_error_response().as_web_response()
