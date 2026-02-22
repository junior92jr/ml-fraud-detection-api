from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "ML Fraud Detection API"
    VERSION: str = "v1"
    DATABASE_URI: str = Field(default="")
    LOG_LEVEL: str = Field(default="WARNING")
    LOGFIRE_TOKEN: str = Field(default="")
    LOGFIRE_SERVICE_NAME: str = Field(default="ml-fraud-detection-api")
    LOGFIRE_ENVIRONMENT: str = Field(default="development")

    model_config = SettingsConfigDict(case_sensitive=True)


class SettingsTest(Settings):
    DATABASE_URI: str = Field(default="", validation_alias="DATABASE_URI_TEST")

    model_config = SettingsConfigDict(case_sensitive=True)


settings = Settings()
settings_test = SettingsTest()
