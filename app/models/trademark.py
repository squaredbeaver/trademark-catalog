from datetime import date
from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints

from app.models.id import generate_id


class Trademark(BaseModel):
    id: str = Field(default_factory=generate_id)
    title: Annotated[str, StringConstraints(min_length=1)]
    description: str | None
    application_number: str
    application_date: date
    registration_date: date
    expiry_date: date
