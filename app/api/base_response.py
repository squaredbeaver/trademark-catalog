from typing import Any

from aiohttp import web
from pydantic import BaseModel

from app.api.codes import HttpCode


class BaseResponse(BaseModel):
    http_code: HttpCode

    @classmethod
    def ok_response(cls, *args: Any, **kwargs: Any) -> 'BaseResponse':
        return cls(http_code=HttpCode.ok)

    @classmethod
    def created_response(cls, *args: Any, **kwargs: Any) -> 'BaseResponse':
        return cls(http_code=HttpCode.created)

    @classmethod
    def conflict_response(cls, *args: Any, **kwargs: Any) -> 'BaseResponse':
        return cls(http_code=HttpCode.conflict)

    @classmethod
    def not_found_response(cls, *args: Any, **kwargs: Any) -> 'BaseResponse':
        return cls(http_code=HttpCode.not_found)

    @classmethod
    def bad_request_response(cls, *args: Any, **kwargs: Any) -> 'BaseResponse':
        return cls(http_code=HttpCode.bad_request)

    @classmethod
    def internal_error_response(cls, *args: Any, **kwargs: Any) -> 'BaseResponse':
        return cls(http_code=HttpCode.internal_error)

    def as_web_response(self) -> web.Response:
        response_data = self.model_dump_json(exclude={'http_code'})
        return web.json_response(text=response_data, status=self.http_code)
