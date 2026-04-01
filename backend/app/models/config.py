"""
配置模型
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, func

from app.db.base import Base


class Config(Base):
    """配置表"""
    
    __tablename__ = "configs"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
