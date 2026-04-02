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

from app.core.config import settings
from app.services.embedding import get_embedding


class QdrantService:
    """Qdrant 服务封装"""

    def __init__(self) -> None:
        if not settings.qdrant_url:
            raise ValueError("请配置 QDRANT_URL 环境变量")
        if not settings.qdrant_api_key:
            raise ValueError("请配置 QDRANT_API_KEY 环境变量")

        self.collection_name = settings.qdrant_collection
        self.client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
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
                size=settings.embedding_dimension,
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
        embedding = get_embedding(original_text, input_type="document")
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
                    vector=get_embedding(original_text, input_type="document"),
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
        query_embedding = get_embedding(query_text, input_type="query")
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=limit,
            score_threshold=threshold,
            with_payload=True,
        )

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
