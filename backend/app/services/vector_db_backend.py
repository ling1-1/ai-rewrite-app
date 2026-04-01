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


class VectorDBBackend(ABC):
    """向量数据库后端抽象基类"""
    
    @abstractmethod
    def search(self, query_text: str, limit: int = 5, threshold: float = 0.7) -> List[Dict[str, Any]]:
        """检索相似文档"""
        pass
    
    @abstractmethod
    def add(self, original_text: str, rewrite_text: str, metadata: List[str]) -> bool:
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
    
    def __init__(self):
        from app.services.viking_rag_service import VikingRAGService
        self.service = VikingRAGService()
    
    def search(self, query_text: str, limit: int = 5, threshold: float = 0.7) -> List[Dict[str, Any]]:
        return self.service.search(query_text, limit=limit)
    
    def add(self, original_text: str, rewrite_text: str, metadata: List[str]) -> bool:
        return self.service.add_single(original_text, rewrite_text, metadata)
    
    def delete(self, doc_id: str) -> bool:
        # VikingDB 暂不支持删除
        return False
    
    def count(self) -> int:
        # VikingDB 暂不支持计数
        return -1


class PgVectorBackend(VectorDBBackend):
    """PostgreSQL + pgvector 后端实现（待实现）"""
    
    def __init__(self):
        # TODO: 实现 pgvector 连接
        pass
    
    def search(self, query_text: str, limit: int = 5, threshold: float = 0.7) -> List[Dict[str, Any]]:
        # TODO: 实现 pgvector 检索
        raise NotImplementedError("PgVectorBackend not implemented yet")
    
    def add(self, original_text: str, rewrite_text: str, metadata: List[str]) -> bool:
        # TODO: 实现 pgvector 添加
        raise NotImplementedError("PgVectorBackend not implemented yet")
    
    def delete(self, doc_id: str) -> bool:
        # TODO: 实现 pgvector 删除
        raise NotImplementedError("PgVectorBackend not implemented yet")
    
    def count(self) -> int:
        # TODO: 实现 pgvector 计数
        raise NotImplementedError("PgVectorBackend not implemented yet")


class QdrantBackend(VectorDBBackend):
    """Qdrant 后端实现（待实现）"""
    
    def __init__(self):
        # TODO: 实现 Qdrant 连接
        pass
    
    def search(self, query_text: str, limit: int = 5, threshold: float = 0.7) -> List[Dict[str, Any]]:
        # TODO: 实现 Qdrant 检索
        raise NotImplementedError("QdrantBackend not implemented yet")
    
    def add(self, original_text: str, rewrite_text: str, metadata: List[str]) -> bool:
        # TODO: 实现 Qdrant 添加
        raise NotImplementedError("QdrantBackend not implemented yet")
    
    def delete(self, doc_id: str) -> bool:
        # TODO: 实现 Qdrant 删除
        raise NotImplementedError("QdrantBackend not implemented yet")
    
    def count(self) -> int:
        # TODO: 实现 Qdrant 计数
        raise NotImplementedError("QdrantBackend not implemented yet")


# 后端工厂
BACKEND_MAP = {
    'vikingdb': VikingDBBackend,
    'pgvector': PgVectorBackend,
    'qdrant': QdrantBackend,
}


def get_vector_db_backend() -> VectorDBBackend:
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
    
    if backend_name not in BACKEND_MAP:
        print(f"⚠️  未知的后端：{backend_name}，使用默认后端：vikingdb")
        backend_name = 'vikingdb'
    
    backend_class = BACKEND_MAP[backend_name]
    print(f"🔧 使用向量数据库后端：{backend_name}")
    
    return backend_class()


# 全局实例
_vector_db_backend: Optional[VectorDBBackend] = None


def init_vector_db():
    """初始化向量数据库"""
    global _vector_db_backend
    _vector_db_backend = get_vector_db_backend()
    return _vector_db_backend


def get_vector_db() -> VectorDBBackend:
    """获取向量数据库实例"""
    global _vector_db_backend
    if _vector_db_backend is None:
        _vector_db_backend = init_vector_db()
    return _vector_db_backend
