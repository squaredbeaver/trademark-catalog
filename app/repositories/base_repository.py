from abc import ABC, abstractmethod
from functools import cached_property
from typing import Any

from pydantic import BaseModel


class BaseRepository(ABC):
    @property
    @abstractmethod
    def table_name(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def fields(self) -> tuple[str, ...]:
        raise NotImplementedError

    @cached_property
    def columns(self) -> str:
        return ', '.join(self.fields)

    def _get_positions(
            self,
            *,
            start: int = 1,
    ) -> str:
        if start < 1:
            raise ValueError('start must be greater than 0')

        end = start + len(self.fields)
        return ', '.join(f'${pos}' for pos in range(start, end))

    def _get_query_args(
            self,
            source: BaseModel,
            *,
            start: int = 0,
    ) -> list[Any]:
        return [getattr(source, field) for field in self.fields[start:]]
