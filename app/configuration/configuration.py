from pydantic import EmailStr, HttpUrl, PostgresDsn, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.enums import Environment


class Configuration(BaseSettings):
    BACKEND_URL: HttpUrl
    DATABASE_URL: PostgresDsn
    EMAIL: EmailStr
    EMAIL_HOST: str
    EMAIL_PASSWORD: SecretStr
    EMAIL_PORT: int
    ENCRYPTION_ALGORITHM: str
    ENCRYPTION_SECRET_KEY: str
    FRONTEND_URL: HttpUrl
    LOGFIRE_TOKEN: str
    ODOO_API_KEY: SecretStr
    ODOO_DB: str
    ODOO_USER: str
    ODOO_URL: HttpUrl

    environment: Environment = Environment.DEVELOPMENT

    model_config = SettingsConfigDict(env_file=".env")


configuration: Configuration = Configuration()  # type: ignore
