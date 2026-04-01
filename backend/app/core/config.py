from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    app_name: str = "JS 论文工作室 API"
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 60 * 24 * 7
    
    # 数据库配置
    database_url: str = ""
    
    # Claude API 配置（火山方舟）
    anthropic_api_key: str = ""
    anthropic_model: str = "doubao-lite-4k-241215"
    anthropic_base_url: str = "https://ark.cn-beijing.volces.com/api/v3"
    anthropic_max_tokens: int = 4096
    anthropic_temperature: float = 0.7
    
    # 豆包 Embedding 配置
    embedding_api_key: str = ""
    embedding_model: str = "doubao-embedding-lite"
    embedding_base_url: str = "https://ark.cn-beijing.volces.com/api/v3"
    embedding_dimension: int = 1536
    
    # RAG 检索配置
    rag_top_k: int = 10
    rag_similarity_threshold: float = 0.7
    
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
        extra='ignore'  # 忽略额外的环境变量
    )


settings = Settings()
