"""
配置模型
"""

from datetime import datetime
import os

from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, func

DATABASE_URL = os.getenv("DATABASE_URL", "")
IS_POSTGRES = "postgresql" in DATABASE_URL

if IS_POSTGRES:
    from sqlalchemy.dialects.postgresql import JSONB
    ConfigValueType = JSONB
else:
    from sqlalchemy import JSON
    ConfigValueType = JSON

from app.db.base import Base


class Config(Base):
    """配置表"""
    
    __tablename__ = "configs"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(ConfigValueType, nullable=False)
    description = Column(Text, nullable=True)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
