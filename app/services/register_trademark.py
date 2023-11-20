from datetime import date
from enum import IntEnum
from logging import Logger
from typing import Annotated

from pydantic import BaseModel, StringConstraints

from app.models.trademark import Trademark
from app.repositories.database_session import DatabaseSession, DatabaseSessionFactory
from app.repositories.trademark import TrademarkRepository


class RegisterTrademarkServiceRequest(BaseModel):
    title: Annotated[str, StringConstraints(min_length=1)]
    description: str | None
    application_number: str
    application_date: date
    registration_date: date
    expiry_date: date


class RegisterTrademarkServiceResponseCode(IntEnum):
    success = 0
    already_registered = 1
    error = 2


class RegisterTrademarkServiceResponse(BaseModel):
    code: RegisterTrademarkServiceResponseCode
    result: Trademark | None = None

    def is_success(self) -> bool:
        return self.code is RegisterTrademarkServiceResponseCode.success

    def is_already_registered(self) -> bool:
        return self.code is RegisterTrademarkServiceResponseCode.already_registered

    def is_error(self) -> bool:
        return self.code is RegisterTrademarkServiceResponseCode.error

    @classmethod
    def success_response(cls, result: Trademark | None) -> 'RegisterTrademarkServiceResponse':
        return cls(code=RegisterTrademarkServiceResponseCode.success, result=result)

    @classmethod
    def already_registered_response(cls) -> 'RegisterTrademarkServiceResponse':
        return cls(code=RegisterTrademarkServiceResponseCode.already_registered)

    @classmethod
    def error_response(cls) -> 'RegisterTrademarkServiceResponse':
        return cls(code=RegisterTrademarkServiceResponseCode.error)


class RegisterTrademarkService:
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
            request: RegisterTrademarkServiceRequest,
    ) -> RegisterTrademarkServiceResponse:
        trademark = Trademark(**request.model_dump())

        async with self._db_session_factory.create_session() as db_session:
            try:
                return await self._register_trademark(trademark, db_session=db_session)
            except Exception as any_error:
                self._logger.exception('RegisterTrademarkService failed with an exception: %s', any_error)
                return RegisterTrademarkServiceResponse.error_response()

    async def _register_trademark(
            self,
            trademark: Trademark,
            db_session: DatabaseSession,
    ) -> RegisterTrademarkServiceResponse:
        existing_trademark = await self._trademark_repository.find_exact(
            title=trademark.title,
            session=db_session,
        )
        if existing_trademark is not None:
            return RegisterTrademarkServiceResponse.already_registered_response()

        await self._trademark_repository.create(
            trademark=trademark,
            session=db_session,
        )

        return RegisterTrademarkServiceResponse.success_response(result=trademark)
