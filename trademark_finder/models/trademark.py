from datetime import date
from typing import Optional

from pydantic import BaseModel, Field

from trademark_finder.utils.helpers import generate_id


class Trademark(BaseModel):
    id: str = Field(default_factory=generate_id)
    title: str
    description: Optional[str]
    application_number: str
    application_date: date
    registration_date: date
    expiry_date: date
