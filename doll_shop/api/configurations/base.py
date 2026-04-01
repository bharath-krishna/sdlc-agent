import logging
from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    title: str = "Doll Shop API"
    prefix: str = "/api"
    debug: bool = True

    postgres_host: str = Field("localhost", validation_alias="POSTGRES_HOST")
    postgres_port: int = Field(5432, validation_alias="POSTGRES_PORT")
    postgres_username: str = Field("postgres", validation_alias="POSTGRES_USERNAME")
    postgres_password: str = Field("WXaobVZ9DI", validation_alias="POSTGRES_PASSWORD")
    postgres_db: str = Field("dollshop", validation_alias="POSTGRES_DB")

    signature_text: str = Field("somesecret", validation_alias="API_SIGNATURE_TEXT")

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_username}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    @property
    def sync_database_url(self) -> str:
        return f"postgresql+psycopg2://{self.postgres_username}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    @property
    def logger(self):
        return logging.getLogger("dollshop")


config = Settings()
