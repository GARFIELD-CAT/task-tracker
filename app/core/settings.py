from pathlib import Path
from typing import Union

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL

ENV_FILE_PATH = Path(__file__).parent.parent.parent / ".env"


class ApiConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH, env_file_encoding="utf-8", extra="ignore"
    )

    project_name: str = "task-tracker"
    project_port: int = 8000
    project_host: str = "127.0.0.1"

    postgres_user: str = "postgres"
    postgres_password: str = "password"
    postgres_db: str = "master"
    postgres_port: int = 5432
    postgres_host: str = "localhost"

    pg_auth: Union[str, URL] = ""

    logger_level: str = "INFO"


settings = ApiConfig()


settings.pg_auth = URL.create(
    "postgresql+asyncpg",
    username=settings.postgres_user,
    password=settings.postgres_password,
    host=settings.postgres_host,
    port=settings.postgres_port,
    database=settings.postgres_db,
)


if __name__ == "__main__":
    print(settings.model_config)
    print(settings)
