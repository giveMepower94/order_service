from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        populate_by_name=True,
        extra="ignore"
    )

    capashino_base_url: str = Field(alias="CAPASHINO_BASE_URL")
    capashino_api_key: str = Field(alias="CAPASHINO_API_KEY")

    database_url: str = Field(alias="POSTGRES_CONNECTION_STRING")

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        if value.startswith("postgres://"):
            return value.replace("postgres://", "postgresql+asyncpg://", 1)
        if value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+asyncpg://", 1)
        return value


settings = settings()
