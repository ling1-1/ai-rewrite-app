from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

# pgvector 扩展
try:
    from pgvector.sqlalchemy import Vector
    VECTOR_AVAILABLE = True
except ImportError:
    VECTOR_AVAILABLE = False
    Vector = None


class RewriteRecord(Base):
    __tablename__ = "rewrite_records"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    
    # 原文和改写结果
    source_text: Mapped[str] = mapped_column(Text, nullable=False)
    result_text: Mapped[str] = mapped_column(Text, nullable=False)
    
    # 向量嵌入（用于 RAG 检索）- pgvector
    embedding: Mapped[list] = mapped_column(
        Vector(1536) if VECTOR_AVAILABLE else Text,
        nullable=True,
        index=VECTOR_AVAILABLE
    )
    
    # 元数据（JSONB 存储额外信息）
    metadata_: Mapped[dict] = mapped_column(
        JSONB,
        default={},
        nullable=True,
        name="metadata"
    )
    
    # 相似度分数（用于记录检索时的相似度）
    similarity_score: Mapped[float] = mapped_column(nullable=True)
    
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

