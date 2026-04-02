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
    
    # 自定义名称（用户可编辑）
    name: Mapped[str] = mapped_column(Text, nullable=True)
    
    # 是否收藏
    is_favorite: Mapped[bool] = mapped_column(default=False, nullable=False)
    
    # 备注
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    
    # 元数据（JSON/JSONB 存储额外信息）
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

    @property
    def is_in_vector_db(self) -> bool:
        metadata = self.metadata_ or {}
        return bool(metadata.get("vector_db_synced"))

    @property
    def vector_db_synced_at(self):
        metadata = self.metadata_ or {}
        return metadata.get("vector_db_synced_at")

    @property
    def vector_db_sync_count(self) -> int:
        metadata = self.metadata_ or {}
        count = metadata.get("vector_db_sync_count", 0)
        try:
            return int(count or 0)
        except (TypeError, ValueError):
            return 0

    @property
    def history_status(self) -> str:
        if self.is_in_vector_db and self.vector_db_sync_count > 1:
            return "updated"
        if self.is_in_vector_db:
            return "synced"
        if self.is_favorite:
            return "favorite"
        return "normal"
