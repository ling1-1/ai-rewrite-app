"""
配置管理服务

支持动态配置 RAG 参数、系统提示词、功能开关等
"""

from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional, Any
import json

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
        if key in ['rag_top_k']:
            return int(config.value)
        elif key in ['rag_similarity_threshold']:
            return float(config.value)
        elif key in ['enable_registration']:
            return config.value.lower() == 'true'
        else:
            return config.value
    
    def set(self, key: str, value: Any, description: str = None) -> None:
        """更新配置值"""
        config = self.db.execute(
            select(Config).where(Config.key == key)
        ).scalar_one_or_none()
        
        if config:
            config.value = str(value)
            if description:
                config.description = description
        else:
            config = Config(
                key=key,
                value=str(value),
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
    
    def is_registration_enabled(self) -> bool:
        """检查是否允许注册"""
        return self.get('enable_registration', True)
