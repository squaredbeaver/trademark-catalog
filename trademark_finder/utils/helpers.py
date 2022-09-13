from datetime import date, datetime
from uuid import uuid4


def datetime_now() -> datetime:
    return datetime.utcnow()


def generate_id() -> str:
    return str(uuid4())


def parse_date(value: str) -> date:
    return date.fromisoformat(value)
