from typing import Literal

from pydantic import (
    computed_field,
)
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"
    PROJECT_NAME: str
    POSTGRES_SERVER: str
    POSTGRES_PORT: int
    POSTGRES_PORT_EXT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    API_KEY: str

    # Services
    ITEMS_SERVICE_HOST: str
    ITEMS_SERVICE_PORT: int | None = None
    ITEMS_SERVICE_API_KEY: str | None = None

    BUSINESS_SERVICE_HOST: str
    BUSINESS_SERVICE_PORT: int | None = None
    BUSINESS_SERVICE_API_KEY: str | None = None

    # Testing
    POSTGRES_DB_TESTING: str

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> MultiHostUrl:
        return MultiHostUrl.build(
            scheme="postgresql+asyncpg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )


class TestSettings(Settings):
    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> MultiHostUrl:
        return MultiHostUrl.build(
            scheme="postgresql+asyncpg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT_EXT,
            path=self.POSTGRES_DB_TESTING,
        )


settings = Settings()  # type: ignore[call-arg]

test_settings = TestSettings()  # type: ignore[call-arg]
