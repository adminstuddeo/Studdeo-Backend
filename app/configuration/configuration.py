from typing import List

from pydantic import HttpUrl, PostgresDsn, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.enums import Environment


class Configuration(BaseSettings):
    BACKEND_URL: HttpUrl
    DATABASE_URL: PostgresDsn
    ENCRYPTION_ALGORITHM: str
    ENCRYPTION_SECRET_KEY: str
    FRONTEND_URL: HttpUrl = HttpUrl("http://localhost:3000")
    ODOO_API_KEY: SecretStr
    ODOO_DB: str
    ODOO_USER: str
    ODOO_URL: HttpUrl

    environment: Environment = Environment.DEVELOPMENT
    allow_origins: List[str] = [
        "http://localhost:3000"
        if environment == Environment.DEVELOPMENT
        else FRONTEND_URL.encoded_string()
    ]

    model_config = SettingsConfigDict(env_file=".env")


configuration: Configuration = Configuration()  # type: ignore
