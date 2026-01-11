import os

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "ML Fraud Detection API"
    VERSION: str = "v1"
    DATABASE_URI: str = os.getenv("DATABASE_URI", "")

    model_config = ConfigDict(case_sensitive=True)


class SettingsTest(Settings):
    DATABASE_URI: str = os.getenv("DATABASE_URI_TEST", "")


settings = Settings()
settings_test = SettingsTest()
