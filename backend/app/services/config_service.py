"""
配置管理服务

支持动态配置 RAG 参数、系统提示词、功能开关等
"""

from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import Any

from app.models.config import Config


class ConfigService:
    """配置服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        config = self.db.execute(
            select(Config).where(Config.key == key)
        ).scalar_one_or_none()
        
        if not config:
            return default
        
        # 根据 key 类型转换
        if key in ['rag_top_k', 'rewrite_max_tokens', 'defense_max_tokens']:
            return int(config.value)
        elif key in ['rag_similarity_threshold']:
            return float(config.value)
        elif key in ['rewrite_temperature', 'defense_temperature']:
            return float(config.value)
        elif key in ['enable_registration']:
            if isinstance(config.value, bool):
                return config.value
            if isinstance(config.value, (int, float)):
                return bool(config.value)
            return str(config.value).strip().lower() in {'true', '1', 'yes', 'on'}
        else:
            return config.value

    def _serialize_value(self, key: str, value: Any) -> Any:
        """按配置项语义存储原生类型，兼容 PostgreSQL JSONB。"""
        if key in {'rag_top_k', 'rewrite_max_tokens', 'defense_max_tokens'}:
            return int(value)
        if key in {'rag_similarity_threshold', 'rewrite_temperature', 'defense_temperature'}:
            return float(value)
        if key == 'enable_registration':
            if isinstance(value, bool):
                return value
            if isinstance(value, (int, float)):
                return bool(value)
            return str(value).strip().lower() in {'true', '1', 'yes', 'on'}
        return value
    
    def set(self, key: str, value: Any, description: str = None) -> None:
        """更新配置值"""
        config = self.db.execute(
            select(Config).where(Config.key == key)
        ).scalar_one_or_none()
        serialized_value = self._serialize_value(key, value)
        
        if config:
            config.value = serialized_value
            if description:
                config.description = description
        else:
            config = Config(
                key=key,
                value=serialized_value,
                description=description
            )
            self.db.add(config)
        
        self.db.commit()
    
    def get_all(self) -> dict:
        """获取所有配置"""
        configs = self.db.execute(select(Config)).scalars().all()
        return {config.key: self.get(config.key) for config in configs}
    
    def get_rag_config(self) -> dict:
        """获取 RAG 配置"""
        return {
            'top_k': self.get('rag_top_k', 3),
            'similarity_threshold': self.get('rag_similarity_threshold', 0.7)
        }
    
    def get_system_prompt(self) -> str:
        """获取系统提示词"""
        return self.get('system_prompt', '')

    def get_defense_system_prompt(self) -> str:
        return self.get('defense_system_prompt', '')

    def get_defense_ppt_prompt(self) -> str:
        return self.get('defense_ppt_prompt', '')

    def get_defense_speech_prompt(self) -> str:
        return self.get('defense_speech_prompt', '')

    def get_model_config(self) -> dict:
        """获取模型配置"""
        return {
            'rewrite_api_key': self.get('rewrite_api_key', ''),
            'rewrite_model': self.get('rewrite_model', ''),
            'rewrite_base_url': self.get('rewrite_base_url', ''),
            'rewrite_max_tokens': self.get('rewrite_max_tokens', None),
            'rewrite_temperature': self.get('rewrite_temperature', None),
            'defense_api_key': self.get('defense_api_key', ''),
            'defense_model': self.get('defense_model', ''),
            'defense_base_url': self.get('defense_base_url', ''),
            'defense_max_tokens': self.get('defense_max_tokens', None),
            'defense_temperature': self.get('defense_temperature', None),
        }

    def get_rewrite_api_key(self, default_api_key: str) -> str:
        return self.get('rewrite_api_key', default_api_key) or default_api_key

    def get_rewrite_model(self, default_model: str) -> str:
        return self.get('rewrite_model', default_model) or default_model

    def get_rewrite_base_url(self, default_base_url: str) -> str:
        return self.get('rewrite_base_url', default_base_url) or default_base_url

    def get_rewrite_max_tokens(self, default_max_tokens: int) -> int:
        value = self.get('rewrite_max_tokens', default_max_tokens)
        return int(value or default_max_tokens)

    def get_rewrite_temperature(self, default_temperature: float) -> float:
        value = self.get('rewrite_temperature', default_temperature)
        return float(value or default_temperature)

    def get_defense_api_key(self, default_api_key: str) -> str:
        return self.get('defense_api_key', default_api_key) or default_api_key

    def get_defense_model(self, default_model: str) -> str:
        return self.get('defense_model', default_model) or default_model

    def get_defense_base_url(self, default_base_url: str) -> str:
        return self.get('defense_base_url', default_base_url) or default_base_url

    def get_defense_max_tokens(self, default_max_tokens: int) -> int:
        value = self.get('defense_max_tokens', default_max_tokens)
        return int(value or default_max_tokens)

    def get_defense_temperature(self, default_temperature: float) -> float:
        value = self.get('defense_temperature', default_temperature)
        return float(value or default_temperature)
    
    def is_registration_enabled(self) -> bool:
        """检查是否允许注册"""
        return self.get('enable_registration', True)
