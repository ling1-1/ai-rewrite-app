from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    app_name: str = "JS 论文工作室 API"
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 60 * 24 * 7
    database_url: str = (
        "postgresql+psycopg://postgres:rewrite_pass@127.0.0.1:5432/rewrite_app"
    )
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-20250514"
    anthropic_base_url: str = "https://api.anthropic.com"
    anthropic_max_tokens: int = 4096
    anthropic_temperature: float = 0.4
    max_upload_size_mb: int = 10

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        if not isinstance(value, str):
            return value

        if value.startswith("postgres://"):
            return value.replace("postgres://", "postgresql+psycopg://", 1)

        if value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+psycopg://", 1)

        return value

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        case_sensitive=False,
    )


settings = Settings()
