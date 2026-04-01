"""
RAG（检索增强生成）服务

用于检索相似的改写记录，构建增强提示词
"""

from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.rewrite_record import RewriteRecord
from app.core.config import settings


class RagService:
    """RAG 检索服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def find_similar_records(
        self,
        embedding: List[float],
        limit: int = None,
        similarity_threshold: float = None
    ) -> List[RewriteRecord]:
        """
        检索相似的改写记录
        
        Args:
            embedding: 查询向量（1536 维）
            limit: 返回数量上限（默认使用配置值）
            similarity_threshold: 相似度阈值（默认使用配置值）
            
        Returns:
            List[RewriteRecord]: 相似的改写记录列表
        """
        limit = limit or settings.rag_top_k
        threshold = similarity_threshold or settings.rag_similarity_threshold
        
        # 检查数据库类型
        db_url = str(self.db.bind.url)
        
        if "postgresql" in db_url:
            # PostgreSQL + pgvector
            return self._find_similar_pgvector(embedding, limit, threshold)
        else:
            # SQLite - 降级到简单检索（按时间倒序）
            return self._find_similar_sqlite(limit)
    
    def _find_similar_pgvector(
        self,
        embedding: List[float],
        limit: int,
        threshold: float
    ) -> List[RewriteRecord]:
        """PostgreSQL + pgvector 向量检索"""
        from sqlalchemy import text
        
        # 将向量转换为字符串格式 '[val1,val2,...]'
        vector_str = '[' + ','.join(str(x) for x in embedding) + ']'
        
        # 使用原始 SQL，避免参数化问题
        sql = f"""
            SELECT 
                id, user_id, source_text, result_text, 
                1 - (embedding <=> '{vector_str}'::vector) as similarity_score
            FROM rewrite_records
            WHERE embedding IS NOT NULL
              AND 1 - (embedding <=> '{vector_str}'::vector) > {threshold}
            ORDER BY embedding <=> '{vector_str}'::vector
            LIMIT {limit}
        """
        
        result = self.db.execute(text(sql)).fetchall()
        
        records = []
        for row in result:
            record = RewriteRecord(
                id=row.id,
                user_id=row.user_id,
                source_text=row.source_text,
                result_text=row.result_text,
                similarity_score=row.similarity_score
            )
            records.append(record)
        
        return records
    
    def _find_similar_sqlite(self, limit: int) -> List[RewriteRecord]:
        """SQLite 降级检索（按时间倒序）"""
        records = self.db.query(RewriteRecord).order_by(
            RewriteRecord.created_at.desc()
        ).limit(limit).all()
        
        return records
    
    def build_rag_prompt(
        self,
        similar_records: List[RewriteRecord],
        user_input: str
    ) -> str:
        """
        构建 RAG 增强提示词
        
        Args:
            similar_records: 相似改写记录列表
            user_input: 用户输入
            
        Returns:
            str: RAG 增强后的提示词
        """
        if not similar_records:
            # 无相似记录，使用基础提示词
            return self._build_base_prompt(user_input)
        
        # 构建示例部分（最多 5 个）
        examples = []
        for i, record in enumerate(similar_records[:5], 1):
            example = f"""示例 {i}:
原文：{record.source_text[:200]}...
改写：{record.result_text[:200]}...
"""
            examples.append(example)
        
        examples_text = "\n\n".join(examples)
        
        # 构建完整提示词
        prompt = f"""你是一个专业的论文改写助手。

参考以下改写示例（按相关性排序）：

{examples_text}

请根据上述示例的风格和技巧，改写以下论文内容：

原文：{user_input}

改写："""
        
        return prompt
    
    def _build_base_prompt(self, user_input: str) -> str:
        """基础提示词（无 RAG 增强）"""
        return f"""你是一个专业的论文改写助手。

请改写以下论文内容，保持原意不变，使表达更学术化、更流畅：

原文：{user_input}

改写："""
