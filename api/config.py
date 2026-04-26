from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "ML Fraud Detection API"
    VERSION: str = "v1"
    DATABASE_URI: str = Field(default="postgres://postgres:postgres@web-db:5432/web")
    DB_GENERATE_SCHEMAS: bool = Field(default=False)
    LOG_LEVEL: str = Field(default="WARNING")
    LOGFIRE_TOKEN: str = Field(default="")
    LOGFIRE_SERVICE_NAME: str = Field(default="ml-fraud-detection-app")
    LOGFIRE_ENVIRONMENT: str = Field(default="development")
    CORS_ALLOW_ORIGINS: list[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"]
    )

    model_config = SettingsConfigDict(case_sensitive=True)


class SettingsTest(Settings):
    DATABASE_URI: str = Field(
        default="postgres://postgres:postgres@web-test-db:5432/web_test",
        validation_alias="DATABASE_URI_TEST",
    )
    LOGFIRE_TOKEN: str = Field(default="", validation_alias="LOGFIRE_TOKEN_TEST")
    DB_GENERATE_SCHEMAS: bool = True

    model_config = SettingsConfigDict(case_sensitive=True)


settings = Settings()
