import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler

from pydantic import EmailStr, Field
from pydantic_settings import BaseSettings

from core.constants import ENV_PATH, STORE_URL_GET_PRODUCT


class Settings(BaseSettings):
    """Settings for current project."""

    #  application
    name_app: str = Field(alias="NAME_APP")
    secret: str = Field(alias="SECRET")
    first_superuser_email: EmailStr = Field(
        alias="FIRST_SUPERUSER_EMAIL"
    )
    first_superuser_password: str = Field(
        alias="FIRST_SUPERUSER_PASSWORD"
    )

    #  telegram
    tg_token: str = Field(alias="TG_TOKEN")

    #  database
    postgres_db: str = Field(alias="POSTGRES_DB")
    postgres_user: str = Field(alias="POSTGRES_USER")
    postgres_password: str = Field(alias="POSTGRES_PASSWORD")
    db_host: str = Field(alias="POSTGRES_SERVER")
    db_port: str = Field(alias="POSTGRES_PORT")

    @property
    def database_url(self) -> str:
        """Return database url from .env ."""
        return "postgresql+asyncpg://{}:{}@{}:{}/{}".format(
            self.postgres_user,
            self.postgres_password,
            self.db_host,
            self.db_port,
            self.postgres_db,
        )

    #  wildberries
    key_store: str = Field(alias="KEY_STORE")

    class Config:
        """Config for the meta class in current settings."""

        env_file = ENV_PATH
        extra = "ignore"


class TestDatabaseSettings(BaseSettings):
    postgres_db: str = Field(alias="TEST_POSTGRES_DB")
    postgres_user: str = Field(alias="TEST_POSTGRES_USER")
    postgres_password: str = Field(alias="TEST_POSTGRES_PASSWORD")
    db_host: str = Field(alias="TEST_POSTGRES_SERVER")
    db_port: str = Field(alias="TEST_POSTGRES_PORT")

    @property
    def database_url(self) -> str:
        """Return database url from .env ."""
        return "postgresql+asyncpg://{}:{}@{}:{}/{}".format(
            self.postgres_user,
            self.postgres_password,
            self.db_host,
            self.db_port,
            self.postgres_db,
        )

    class Config:
        """Config for the meta class in current settings."""

        env_file = ENV_PATH
        extra = "ignore"


def configure_logging(log_dir: Path, log_file: Path, log_format: str) -> None:
    """Setttings logging from this project."""
    log_dir.mkdir(exist_ok=True)
    rotating_handler: RotatingFileHandler = RotatingFileHandler(
        log_file, maxBytes=10**6, backupCount=5
    )
    rotating_handler.setFormatter(log_format)
    project_logger = logging.getLogger(log_file.stem)
    project_logger.setLevel(logging.INFO)
    project_logger.addHandler(rotating_handler)
    project_logger.addHandler(logging.StreamHandler())


settings = Settings()
test_database_settings = TestDatabaseSettings()
