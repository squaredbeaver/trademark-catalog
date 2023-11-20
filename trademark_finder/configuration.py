from typing import Literal

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings


class AppConfig(BaseSettings):
    port: int = 8080
    postgres_dsn: PostgresDsn
    logging_level: Literal['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'] = 'INFO'
