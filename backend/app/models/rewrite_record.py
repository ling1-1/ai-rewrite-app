from datetime import datetime
import os

from sqlalchemy import DateTime, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

# 检测数据库类型
DATABASE_URL = os.getenv("DATABASE_URL", "")
IS_POSTGRES = "postgresql" in DATABASE_URL

# PostgreSQL 用 JSONB，SQLite 用 JSON
if IS_POSTGRES:
    from sqlalchemy.dialects.postgresql import JSONB
    MetadataType = JSONB
else:
    from sqlalchemy import JSON
    MetadataType = JSON


class RewriteRecord(Base):
    __tablename__ = "rewrite_records"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    
    # 原文和改写结果
    source_text: Mapped[str] = mapped_column(Text, nullable=False)
    result_text: Mapped[str] = mapped_column(Text, nullable=False)
    
    # 元数据（JSON/JSONB 存储额外信息）
    # 存储：用户名、使用模型、使用时间等
    metadata_: Mapped[dict] = mapped_column(
        MetadataType,
        default={},
        nullable=True,
        name="metadata"
    )
    
    # 大模型原始响应
    response: Mapped[str] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        onupdate=func.now()
    )

    user = relationship("User", back_populates="records")

