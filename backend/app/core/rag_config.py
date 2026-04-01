"""
RAG 配置管理

可配置的参数：
- top_k: 检索相似记录数量（默认 3-5 条）
- similarity_threshold: 相似度阈值（默认 0.7）
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class RAGConfig(BaseSettings):
    """RAG 检索配置"""
    
    # 检索相似记录数量（3-5 条可调）
    top_k: int = 3
    
    # 相似度阈值（0-1 之间）
    similarity_threshold: float = 0.7
    
    # 是否启用 RAG
    enabled: bool = True
    
    model_config = SettingsConfigDict(
        env_file=".env",
        extra='ignore'  # 忽略额外的环境变量
    )


# 全局配置实例
rag_config = RAGConfig()


def get_rag_config() -> RAGConfig:
    """获取 RAG 配置"""
    return rag_config


def update_rag_config(top_k: int = None, similarity_threshold: float = None, enabled: bool = None):
    """更新 RAG 配置"""
    if top_k is not None:
        if not (1 <= top_k <= 10):
            raise ValueError("top_k 必须在 1-10 之间")
        rag_config.top_k = top_k
    
    if similarity_threshold is not None:
        if not (0 <= similarity_threshold <= 1):
            raise ValueError("similarity_threshold 必须在 0-1 之间")
        rag_config.similarity_threshold = similarity_threshold
    
    if enabled is not None:
        rag_config.enabled = enabled
    
    return rag_config
