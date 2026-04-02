"""
向量数据库抽象层

支持多种向量数据库后端，支持平滑迁移：
- VikingDB (火山)
- pgvector (PostgreSQL)
- Qdrant
- Milvus
- 其他...

使用方式：
1. 在 .env 中配置 VECTOR_DB_BACKEND
2. 实现 VectorDBBackend 接口
3. 自动切换后端
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import os
from sqlalchemy.orm import Session


class VectorDBBackend(ABC):
    """向量数据库后端抽象基类"""
    
    @abstractmethod
    def search(self, query_text: str, limit: int = 5, threshold: float = 0.7) -> List[Dict[str, Any]]:
        """检索相似文档"""
        pass
    
    @abstractmethod
    def add(
        self,
        original_text: str,
        rewrite_text: str,
        metadata: List[str],
        doc_id: Optional[str] = None,
        extra_payload: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """添加文档"""
        pass
    
    @abstractmethod
    def delete(self, doc_id: str) -> bool:
        """删除文档"""
        pass
    
    @abstractmethod
    def count(self) -> int:
        """返回文档总数"""
        pass


class VikingDBBackend(VectorDBBackend):
    """VikingDB 后端实现"""
    
    def __init__(self, db: Session | None = None):
        from app.services.viking_rag_service import VikingRAGService
        self.service = VikingRAGService()
    
    def search(self, query_text: str, limit: int = 5, threshold: float = 0.7) -> List[Dict[str, Any]]:
        return self.service.search(query_text, limit=limit)
    
    def add(
        self,
        original_text: str,
        rewrite_text: str,
        metadata: List[str],
        doc_id: Optional[str] = None,
        extra_payload: Optional[Dict[str, Any]] = None,
    ) -> bool:
        return self.service.add_single(original_text, rewrite_text, metadata)
    
    def delete(self, doc_id: str) -> bool:
        # VikingDB 暂不支持删除
        return False
    
    def count(self) -> int:
        # VikingDB 暂不支持计数
        return -1


class PgVectorBackend(VectorDBBackend):
    """PostgreSQL + pgvector 后端实现（待实现）"""
    
    def __init__(self, db: Session | None = None):
        # TODO: 实现 pgvector 连接
        pass
    
    def search(self, query_text: str, limit: int = 5, threshold: float = 0.7) -> List[Dict[str, Any]]:
        # TODO: 实现 pgvector 检索
        raise NotImplementedError("PgVectorBackend not implemented yet")
    
    def add(
        self,
        original_text: str,
        rewrite_text: str,
        metadata: List[str],
        doc_id: Optional[str] = None,
        extra_payload: Optional[Dict[str, Any]] = None,
    ) -> bool:
        # TODO: 实现 pgvector 添加
        raise NotImplementedError("PgVectorBackend not implemented yet")
    
    def delete(self, doc_id: str) -> bool:
        # TODO: 实现 pgvector 删除
        raise NotImplementedError("PgVectorBackend not implemented yet")
    
    def count(self) -> int:
        # TODO: 实现 pgvector 计数
        raise NotImplementedError("PgVectorBackend not implemented yet")


class QdrantBackend(VectorDBBackend):
    """Qdrant 后端实现"""
    
    def __init__(self, db: Session | None = None):
        from app.services.qdrant_service import QdrantService

        self.service = QdrantService(db=db)
    
    def search(self, query_text: str, limit: int = 5, threshold: float = 0.7) -> List[Dict[str, Any]]:
        return self.service.search(query_text, limit=limit, threshold=threshold)
    
    def add(
        self,
        original_text: str,
        rewrite_text: str,
        metadata: List[str],
        doc_id: Optional[str] = None,
        extra_payload: Optional[Dict[str, Any]] = None,
    ) -> bool:
        self.service.add_document(
            original_text,
            rewrite_text,
            metadata=metadata,
            extra_payload=extra_payload,
            doc_id=doc_id,
        )
        return True
    
    def delete(self, doc_id: str) -> bool:
        return self.service.delete(doc_id)
    
    def count(self) -> int:
        return self.service.count()


# 后端工厂
BACKEND_MAP = {
    'vikingdb': VikingDBBackend,
    'pgvector': PgVectorBackend,
    'qdrant': QdrantBackend,
}


def get_vector_db_backend(db: Session | None = None) -> VectorDBBackend:
    """
    获取向量数据库后端实例
    
    配置方式：
    1. 在 .env 中设置 VECTOR_DB_BACKEND=vikingdb
    2. 支持的后端：vikingdb, pgvector, qdrant, milvus
    
    平滑迁移步骤：
    1. 实现新的后端类（如 MilvusBackend）
    2. 在 BACKEND_MAP 中注册
    3. 修改 .env 配置
    4. 重启服务
    """
    backend_name = os.getenv('VECTOR_DB_BACKEND', 'vikingdb').lower()
    if db is not None:
        try:
            from app.core.config import settings
            from app.services.config_service import ConfigService

            config_service = ConfigService(db)
            backend_name = config_service.get_vector_db_backend(settings.vector_db_backend).lower()
        except Exception as exc:
            print(f"⚠️  获取向量数据库配置失败，使用环境变量默认值：{exc}")
    
    if backend_name not in BACKEND_MAP:
        print(f"⚠️  未知的后端：{backend_name}，使用默认后端：vikingdb")
        backend_name = 'vikingdb'
    
    backend_class = BACKEND_MAP[backend_name]
    print(f"🔧 使用向量数据库后端：{backend_name}")
    
    return backend_class(db=db)


# 全局实例
_vector_db_backend: Optional[VectorDBBackend] = None


def init_vector_db(db: Session | None = None):
    """初始化向量数据库"""
    global _vector_db_backend
    _vector_db_backend = get_vector_db_backend(db=db)
    return _vector_db_backend


def get_vector_db(db: Session | None = None) -> VectorDBBackend:
    """获取向量数据库实例"""
    global _vector_db_backend
    if db is not None:
        return get_vector_db_backend(db=db)
    if _vector_db_backend is None:
        _vector_db_backend = init_vector_db()
    return _vector_db_backend
