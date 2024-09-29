from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_core import MultiHostUrl
from pydantic import computed_field, PostgresDsn


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="UTF-8", case_sensitive=True
    )

    TEMPLATES_DIR: str = "app/jinja_templates/"

    ADMIN_TG_ID: str

    LANDING_URL: str = "www.google.com"
    TERMS_URL: str = "https://docs.google.com/document/d/12hML4G7ZG4ci_Zi_VrpeNsP1XpczrWm0bu7wTdwvVhk/edit?usp=sharing"
    APP_URL: str = "t.me/"

    POSTGRES_DB: str = "postgres"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "1234"
    POSTGRES_PORT: int = 5432
    POSTGRES_HOST: str = "db"

    REDIS_URL: str = "redis://redis:6379"

    ADMIN_CHAT_ID: int

    YOUMONEY_APP_ID: str
    YOUMONEY_SECRET_KEY: str

    TG_TOKEN: str

    GS_SCOPES: List[str] = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
    GS_SPREADSHEET_URL: str = ""
    GS_CREDENTIALS_FILE: str = "app/configs/service_account.json"

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return MultiHostUrl.build(
            scheme="postgresql+asyncpg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )


settings = Settings()  # type: ignore
