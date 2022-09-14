from typing import Literal

from pydantic import BaseSettings, PostgresDsn


class AppConfig(BaseSettings):
    port: int = 8080
    postgres_dsn: PostgresDsn
    logging_level: Literal['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'] = 'INFO'
