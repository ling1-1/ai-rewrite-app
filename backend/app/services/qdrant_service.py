"""
Qdrant 向量数据库服务

负责：
- 自动初始化 collection
- 写入改写记录
- 语义检索相似记录
"""

from __future__ import annotations

import uuid
from typing import Any, Dict, List

from qdrant_client import QdrantClient
from qdrant_client.http import models
from sqlalchemy.orm import Session

from app.core.config import settings
from app.services.embedding import get_embedding


class QdrantService:
    """Qdrant 服务封装"""

    def __init__(self, db: Session | None = None) -> None:
        self.db = db
        qdrant_url = settings.qdrant_url
        qdrant_api_key = settings.qdrant_api_key
        collection_name = settings.qdrant_collection
        embedding_dimension = settings.embedding_dimension

        if db:
            try:
                from app.services.config_service import ConfigService

                config_service = ConfigService(db)
                qdrant_url = config_service.get_qdrant_url(settings.qdrant_url)
                qdrant_api_key = config_service.get_qdrant_api_key(settings.qdrant_api_key)
                collection_name = config_service.get_qdrant_collection(settings.qdrant_collection)
                embedding_dimension = config_service.get_embedding_dimension(settings.embedding_dimension)
            except Exception as exc:
                print(f"⚠️  获取 Qdrant 配置失败，使用环境变量默认值：{exc}")

        if not qdrant_url:
            raise ValueError("请配置 QDRANT_URL 环境变量")
        if not qdrant_api_key:
            raise ValueError("请配置 QDRANT_API_KEY 环境变量")

        self.collection_name = collection_name
        self.embedding_dimension = embedding_dimension
        self.client = QdrantClient(
            url=qdrant_url,
            api_key=qdrant_api_key,
            timeout=30.0,
        )
        self._ensure_collection()

    def _ensure_collection(self) -> None:
        collections = self.client.get_collections().collections
        exists = any(collection.name == self.collection_name for collection in collections)
        if exists:
            return

        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=models.VectorParams(
                size=self.embedding_dimension,
                distance=models.Distance.COSINE,
            ),
        )

    def add_document(
        self,
        original_text: str,
        rewrite_text: str,
        metadata: List[str] | None = None,
        extra_payload: Dict[str, Any] | None = None,
        doc_id: str | None = None,
    ) -> str:
        embedding = get_embedding(original_text, input_type="document", db=self.db)
        point_id = doc_id or str(uuid.uuid4())
        payload: Dict[str, Any] = {
            "original_text": original_text,
            "rewrite_text": rewrite_text,
            "metadata": metadata or [],
        }
        if extra_payload:
            payload.update(extra_payload)

        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                models.PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload=payload,
                )
            ],
            wait=True,
        )
        return point_id

    def add_documents(self, documents: List[Dict[str, Any]]) -> int:
        points: List[models.PointStruct] = []
        for document in documents:
            original_text = document.get("original_text", "")
            rewrite_text = document.get("rewrite_text", "")
            metadata = document.get("metadata", [])
            extra_payload = document.get("payload", {})

            points.append(
                models.PointStruct(
                    id=document.get("id") or str(uuid.uuid4()),
                    vector=get_embedding(original_text, input_type="document", db=self.db),
                    payload={
                        "original_text": original_text,
                        "rewrite_text": rewrite_text,
                        "metadata": metadata,
                        **extra_payload,
                    },
                )
            )

        if not points:
            return 0

        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
            wait=True,
        )
        return len(points)

    def search(
        self,
        query_text: str,
        limit: int = 5,
        threshold: float = 0.7,
    ) -> List[Dict[str, Any]]:
        query_embedding = get_embedding(query_text, input_type="query", db=self.db)
        results = self._query_points(query_embedding, limit=limit, threshold=threshold)

        documents: List[Dict[str, Any]] = []
        for item in results:
            payload = item.payload or {}
            documents.append(
                {
                    "id": str(item.id),
                    "original_text": payload.get("original_text", ""),
                    "rewrite_text": payload.get("rewrite_text", ""),
                    "metadata": payload.get("metadata", []),
                    "score": float(item.score or 0.0),
                    "payload": payload,
                }
            )
        return documents

    def _query_points(
        self,
        query_embedding: List[float],
        limit: int,
        threshold: float,
    ):
        # 新版 qdrant-client 推荐接口
        if hasattr(self.client, "query_points"):
            response = self.client.query_points(
                collection_name=self.collection_name,
                query=query_embedding,
                limit=limit,
                score_threshold=threshold,
                with_payload=True,
            )
            if hasattr(response, "points"):
                return response.points
            if isinstance(response, dict):
                return response.get("points") or response.get("result", {}).get("points", [])
            return response

        # 旧版兼容
        if hasattr(self.client, "search"):
            return self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=limit,
                score_threshold=threshold,
                with_payload=True,
            )

        raise AttributeError("当前 qdrant-client 版本不支持 query_points/search")

    def delete(self, doc_id: str) -> bool:
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=models.PointIdsList(points=[doc_id]),
            wait=True,
        )
        return True

    def count(self) -> int:
        return int(
            self.client.count(
                collection_name=self.collection_name,
                exact=True,
            ).count
        )
