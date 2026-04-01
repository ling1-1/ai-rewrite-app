# 🏆 AI 论文改写网站 - RAG 架构升级方案

**版本**: v2.0  
**日期**: 2026-04-01  
**状态**: 待实施

---

## 📊 现状分析

### 当前架构（v1.0）

```
用户输入 → Claude API → 返回结果
            ↓
        SQLite 存储（本地）
```

**问题**：
1. ❌ 无向量检索能力（无法 RAG 增强）
2. ❌ 数据存储在本地（Hugging Face 重启丢失）
3. ❌ 无历史数据复用（每次都是独立改写）
4. ❌ 无法支持后续模型训练

### 现有代码结构

```
breeze1012-project/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI 入口（CORS 配置待更新）
│   │   ├── api/
│   │   │   └── routes/
│   │   │       ├── auth.py      # 认证路由 ✅
│   │   │       ├── rewrite.py   # 改写路由 ✅
│   │   │       └── history.py   # 历史路由 ✅
│   │   ├── models/
│   │   │   ├── user.py          # 用户模型 ✅
│   │   │   └── rewrite_record.py # 改写记录模型（待扩展）
│   │   ├── schemas/
│   │   │   ├── auth.py          # 认证 Schema ✅
│   │   │   └── rewrite.py       # 改写 Schema（待扩展）
│   │   ├── services/
│   │   │   ├── rewrite.py       # 改写服务（待扩展 RAG）
│   │   │   └── file_extract.py  # 文件提取 ✅
│   │   ├── db/
│   │   │   ├── session.py       # 数据库连接（待更新）
│   │   │   └── base.py          # Base 模型 ✅
│   │   └── core/
│   │       └── config.py        # 配置管理（待扩展）
│   └── requirements.txt         # Python 依赖（待添加）
├── frontend/
│   └── src/
│       ├── views/
│       │   └── WorkspaceView.vue # 工作区 ✅
│       └── api/
│           └── http.js          # HTTP 客户端 ✅
└── api/
    └── index.py                 # Vercel 适配层 ✅
```

---

## 🎯 目标架构（v2.0）

### RAG 完整流程

```
┌─────────────────────────────────────────────────────────┐
│  用户输入（论文原文）                                     │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  ① 向量化（豆包 Embedding）                               │
│     - 模型：doubao-embedding-lite                        │
│     - 维度：1536                                         │
│     - 成本：¥0.0007/千 tokens                            │
│     - 延迟：<100ms                                       │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  ② 向量检索（Neon pgvector）                             │
│     - 检索最相似的 5-10 组示例                             │
│     - 查询延迟：<50ms（IVFFlat 索引）                      │
│     - 相似度阈值：>0.7                                   │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  ③ RAG 提示词构建                                         │
│     - 示例 + 用户输入组合                                │
│     - System Prompt 增强                                 │
│     - Few-shot Learning                                │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  ④ Claude API 改写                                        │
│     - 模型：doubao-lite-4k-241215                        │
│     - 成本：约¥0.01/次                                   │
│     - 延迟：1-3 秒                                        │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  ⑤ 结果返回 + 存储                                        │
│     - 返回前端展示                                       │
│     - 存储到 Neon（热数据）                               │
│     - 向量化后存入数据库                                 │
└────────────────────┬────────────────────────────────────┘
                     │ 每月自动归档
                     ▼
┌─────────────────────────────────────────────────────────┐
│  ⑥ Hugging Face Datasets（冷数据）                       │
│     - Parquet 格式存储                                   │
│     - 用于后续模型训练                                   │
│     - 无限制容量                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 🛠️ 技术选型

### 数据库层

| 组件 | 选型 | 理由 |
|------|------|------|
| **热数据存储** | Neon PostgreSQL | 免费 512MB，支持 pgvector |
| **向量检索** | pgvector 0.7.0 | PostgreSQL 扩展，无需额外服务 |
| **冷数据归档** | Hugging Face Datasets | 免费无限制，适合训练 |

### 向量化服务

| 服务 | 选型 | 理由 |
|------|------|------|
| **Embedding API** | 火山方舟 - 豆包 | 与 Claude API 同平台，延迟低 |
| **模型** | doubao-embedding-lite | 1536 维度，性价比高 |
| **成本** | ¥0.0007/千 tokens | 1 万次约¥7 |

### 索引策略

```sql
-- 向量索引（IVFFlat，适合 10 万级向量）
CREATE INDEX ON rewrite_records 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- 复合索引（支持时间范围查询）
CREATE INDEX idx_created_at ON rewrite_records(created_at);
CREATE INDEX idx_user_id ON rewrite_records(user_id);
```

---

## 📋 实施步骤

### 阶段 1：数据库迁移（优先级：🔴 高）

#### 1.1 创建 Neon 数据库

**操作**：
1. 访问 https://neon.tech 注册
2. Create Project → `ai-rewrite-app`
3. Region: `aws-ap-southeast-1` (新加坡)
4. 获取连接字符串

**输出**：
```
postgresql://user:password@host.region.aws.neon.tech/rewrite_app?sslmode=require
```

#### 1.2 更新数据库模型

**文件**: `backend/app/models/rewrite_record.py`

**修改**：
```python
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Text, func, Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

# pgvector 扩展
from pgvector.sqlalchemy import Vector

class RewriteRecord(Base):
    __tablename__ = "rewrite_records"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    
    # 原文和改写结果
    source_text: Mapped[str] = mapped_column(Text, nullable=False)
    result_text: Mapped[str] = mapped_column(Text, nullable=False)
    
    # 新增：向量嵌入（用于 RAG 检索）
    embedding: Mapped[list] = mapped_column(Vector(1536), nullable=True, index=True)
    
    # 新增：元数据（JSONB 存储额外信息）
    metadata_: Mapped[dict] = mapped_column(
        JSONB, 
        default={},
        nullable=True,
        name="metadata"
    )
    
    # 新增：相似度分数（用于记录检索时的相似度）
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
```

#### 1.3 更新数据库会话

**文件**: `backend/app/db/session.py`

**修改**：
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# 添加连接池配置（生产环境必需）
engine = create_engine(
    settings.database_url,
    pool_size=10,           # 连接池大小
    max_overflow=20,        # 最大溢出连接数
    pool_pre_ping=True,     # 自动检测失效连接
    pool_recycle=3600,      # 1 小时回收连接
    future=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

#### 1.4 更新配置文件

**文件**: `backend/app/core/config.py`

**修改**：
```python
from pathlib import Path
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    app_name: str = "JS 论文工作室 API"
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 60 * 24 * 7
    
    # 数据库配置（更新为 Neon）
    database_url: str = ""  # 从环境变量读取
    
    # Claude API 配置
    anthropic_api_key: str = ""
    anthropic_model: str = "doubao-lite-4k-241215"
    anthropic_base_url: str = "https://ark.cn-beijing.volces.com/api/v3"
    anthropic_max_tokens: int = 4096
    anthropic_temperature: float = 0.7
    
    # 新增：豆包 Embedding 配置
    embedding_api_key: str = ""  # 与 Claude API Key 相同（火山方舟）
    embedding_model: str = "doubao-embedding-lite"
    embedding_base_url: str = "https://ark.cn-beijing.volces.com/api/v3"
    embedding_dimension: int = 1536
    
    # RAG 检索配置
    rag_top_k: int = 10          # 检索 Top K 个相似示例
    rag_similarity_threshold: float = 0.7  # 相似度阈值
    max_upload_size_mb: int = 10

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        if not isinstance(value, str):
            return value
        if value.startswith("postgres://"):
            return value.replace("postgres://", "postgresql+psycopg://", 1)
        if value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+psycopg://", 1)
        return value

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        case_sensitive=False,
    )

settings = Settings()
```

#### 1.5 添加依赖

**文件**: `backend/requirements.txt`

**新增**：
```
pgvector>=0.2.0
psycopg2-binary>=2.9.9  # 仅本地开发使用，生产环境用 psycopg
```

---

### 阶段 2：向量化服务（优先级：🔴 高）

#### 2.1 创建 Embedding 服务

**新文件**: `backend/app/services/embedding.py`

```python
import httpx
from app.core.config import settings

class EmbeddingServiceError(Exception):
    pass

def get_embedding(text: str) -> list:
    """
    获取文本的向量嵌入（使用豆包 Embedding API）
    
    Args:
        text: 输入文本
        
    Returns:
        list: 1536 维向量
        
    Raises:
        EmbeddingServiceError: API 调用失败
    """
    if not settings.embedding_api_key:
        raise EmbeddingServiceError("尚未配置 Embedding API Key")
    
    url = f"{settings.embedding_base_url.rstrip('/')}/embeddings"
    payload = {
        "model": settings.embedding_model,
        "input": text.strip(),
    }
    headers = {
        "Authorization": f"Bearer {settings.embedding_api_key}",
        "content-type": "application/json",
    }
    
    try:
        response = httpx.post(url, json=payload, headers=headers, timeout=30.0)
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        message = _extract_error_message(exc.response)
        raise EmbeddingServiceError(f"Embedding API 请求失败：{message}") from exc
    except httpx.HTTPError as exc:
        raise EmbeddingServiceError("无法连接 Embedding API") from exc
    
    data = response.json()
    if "data" not in data or len(data["data"]) == 0:
        raise EmbeddingServiceError("Embedding API 返回空结果")
    
    return data["data"][0]["embedding"]


def _extract_error_message(response: httpx.Response) -> str:
    try:
        payload = response.json()
    except ValueError:
        return response.text or f"HTTP {response.status_code}"
    
    error = payload.get("error", {})
    if isinstance(error, dict):
        return error.get("message") or error.get("type") or f"HTTP {response.status_code}"
    
    return str(error) or f"HTTP {response.status_code}"
```

---

### 阶段 3：RAG 检索服务（优先级：🔴 高）

#### 3.1 创建 RAG 服务

**新文件**: `backend/app/services/rag.py`

```python
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.rewrite_record import RewriteRecord

class RagService:
    """RAG（检索增强生成）服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def find_similar_records(
        self,
        embedding: List[float],
        limit: int = 10,
        similarity_threshold: float = 0.7
    ) -> List[RewriteRecord]:
        """
        检索相似的改写记录
        
        Args:
            embedding: 查询向量（1536 维）
            limit: 返回数量上限
            similarity_threshold: 相似度阈值（0-1）
            
        Returns:
            List[RewriteRecord]: 相似的改写记录列表
        """
        query = text("""
            SELECT 
                id, user_id, source_text, result_text, 
                1 - (embedding <=> :vec) as similarity_score
            FROM rewrite_records
            WHERE embedding IS NOT NULL
              AND 1 - (embedding <=> :vec) > :threshold
            ORDER BY embedding <=> :vec
            LIMIT :limit
        """)
        
        params = {
            "vec": embedding,
            "limit": limit,
            "threshold": 1 - similarity_threshold  # pgvector 使用距离，1-similarity
        }
        
        result = self.db.execute(query, params).fetchall()
        
        # 转换为 RewriteRecord 对象（带 similarity_score）
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
        
        # 构建示例部分
        examples = []
        for i, record in enumerate(similar_records[:5], 1):  # 最多 5 个示例
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
```

---

### 阶段 4：更新改写服务（优先级：🔴 高）

#### 4.1 重写 RewriteService

**文件**: `backend/app/services/rewrite.py`

**修改**：
```python
import httpx
from typing import Optional, List
from app.core.config import settings
from app.services.embedding import get_embedding, EmbeddingServiceError
from app.services.rag import RagService
from sqlalchemy.orm import Session

class RewriteServiceError(Exception):
    pass

SYSTEM_PROMPT = """
你是"JS 论文工作室"的论文改写助手。

你的任务是将用户输入的中文论文内容进行学术化改写和表达优化，但必须遵守以下规则：
1. 保持原意、事实、结论和逻辑结构不变。
2. 优先改写句式、连接方式和表述节奏，使表达更自然、更像人工撰写的论文文本。
3. 保留专业术语、专有名词、数据、年份、引用标记和关键概念，不要凭空增删。
4. 输出应偏向正式、清晰、流畅的中文书面学术表达。
5. 不要附加解释、分析、标题、备注、项目符号或引号。
6. 只返回改写后的正文内容。
""".strip()

def rewrite_text(
    source_text: str,
    db: Optional[Session] = None,
    use_rag: bool = True
) -> str:
    """
    改写文本（支持 RAG 增强）
    
    Args:
        source_text: 原文
        db: 数据库会话（用于 RAG 检索）
        use_rag: 是否启用 RAG 增强
        
    Returns:
        str: 改写后的文本
    """
    # 1. RAG 检索（如果启用且有数据库）
    prompt = source_text
    if use_rag and db:
        try:
            # 1.1 生成查询向量
            query_embedding = get_embedding(source_text)
            
            # 1.2 检索相似记录
            rag_service = RagService(db)
            similar_records = rag_service.find_similar_records(
                query_embedding,
                limit=settings.rag_top_k,
                similarity_threshold=settings.rag_similarity_threshold
            )
            
            # 1.3 构建 RAG 提示词
            if similar_records:
                prompt = rag_service.build_rag_prompt(similar_records, source_text)
        except EmbeddingServiceError:
            # Embedding 失败，降级到基础提示词
            pass
    
    # 2. 调用 Claude API
    if not settings.anthropic_api_key:
        raise RewriteServiceError("尚未配置 Anthropic API Key")
    
    url = f"{settings.anthropic_base_url.rstrip('/')}/v1/messages"
    payload = {
        "model": settings.anthropic_model,
        "max_tokens": settings.anthropic_max_tokens,
        "temperature": settings.anthropic_temperature,
        "system": SYSTEM_PROMPT,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
    }
    headers = {
        "Authorization": f"Bearer {settings.anthropic_api_key}",
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    
    try:
        response = httpx.post(url, json=payload, headers=headers, timeout=90.0)
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        message = _extract_error_message(exc.response)
        raise RewriteServiceError(f"Claude API 请求失败：{message}") from exc
    except httpx.HTTPError as exc:
        raise RewriteServiceError("无法连接 Claude API") from exc
    
    data = response.json()
    content = data.get("content", [])
    result = "\n".join(
        item.get("text", "").strip()
        for item in content
        if item.get("type") == "text" and item.get("text")
    ).strip()
    
    if not result:
        raise RewriteServiceError("Claude API 已返回响应，但没有解析到可用文本")
    
    return result


def save_rewrite_record(
    db: Session,
    user_id: int,
    source_text: str,
    result_text: str
) -> int:
    """
    保存改写记录（带向量嵌入）
    
    Args:
        db: 数据库会话
        user_id: 用户 ID
        source_text: 原文
        result_text: 改写结果
        
    Returns:
        int: 记录 ID
    """
    from app.models.rewrite_record import RewriteRecord
    
    try:
        # 生成向量嵌入（使用改写结果）
        embedding = get_embedding(result_text)
    except EmbeddingServiceError:
        embedding = None
    
    record = RewriteRecord(
        user_id=user_id,
        source_text=source_text,
        result_text=result_text,
        embedding=embedding
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    
    return record.id


def _extract_error_message(response: httpx.Response) -> str:
    try:
        payload = response.json()
    except ValueError:
        return response.text or f"HTTP {response.status_code}"
    
    error = payload.get("error", {})
    if isinstance(error, dict):
        return error.get("message") or error.get("type") or f"HTTP {response.status_code}"
    
    return str(error) or f"HTTP {response.status_code}"
```

---

### 阶段 5：更新 API 路由（优先级：🟡 中）

#### 5.1 更新 Rewrite 路由

**文件**: `backend/app/api/routes/rewrite.py`

**修改**：
```python
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.rewrite_record import RewriteRecord
from app.models.user import User
from app.schemas.rewrite import (
    FileExtractResponse, 
    RewriteRequest, 
    RewriteResponse,
    RewriteRecordSchema  # 新增
)
from app.services.file_extract import FileExtractError, extract_text_from_upload
from app.services.rewrite import (
    RewriteServiceError, 
    rewrite_text,
    save_rewrite_record  # 新增
)

router = APIRouter()

@router.post("", response_model=RewriteResponse)
def create_rewrite(
    payload: RewriteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """改写文本（RAG 增强）"""
    if not payload.source_text.strip():
        raise HTTPException(status_code=400, detail="原文不能为空")

    try:
        # 启用 RAG 增强
        result_text = rewrite_text(
            payload.source_text,
            db=db,
            use_rag=True
        )
    except RewriteServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    # 保存记录（带向量嵌入）
    record_id = save_rewrite_record(
        db=db,
        user_id=current_user.id,
        source_text=payload.source_text,
        result_text=result_text
    )

    return {
        "id": record_id,
        "source_text": payload.source_text,
        "result_text": result_text,
    }

@router.post("/extract-file", response_model=FileExtractResponse)
def extract_file_content(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """从文件提取文本"""
    del current_user

    try:
        source_text = extract_text_from_upload(file)
    except FileExtractError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "filename": file.filename or "未命名文件",
        "source_text": source_text,
        "char_count": len(source_text),
    }

@router.get("/records", response_model=List[RewriteRecordSchema])
def list_rewrite_records(
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取用户改写记录列表"""
    records = db.query(RewriteRecord).filter(
        RewriteRecord.user_id == current_user.id
    ).order_by(
        RewriteRecord.created_at.desc()
    ).offset(offset).limit(limit).all()
    
    return records
```

---

### 阶段 6：数据库初始化脚本（优先级：🟡 中）

#### 6.1 创建迁移脚本

**新文件**: `backend/scripts/init_db.py`

```python
#!/usr/bin/env python3
"""
数据库初始化脚本

功能：
1. 创建 pgvector 扩展
2. 创建数据表
3. 创建索引
"""

import sys
from pathlib import Path

# 添加后端路径
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from sqlalchemy import text
from app.db.session import engine
from app.db.base import Base
from app.models.rewrite_record import RewriteRecord
from app.models.user import User

def init_database():
    """初始化数据库"""
    print("🔧 开始初始化数据库...")
    
    with engine.connect() as conn:
        # 1. 创建 pgvector 扩展
        print("📦 创建 pgvector 扩展...")
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        conn.commit()
        print("✅ pgvector 扩展创建成功")
        
        # 2. 创建数据表
        print("📋 创建数据表...")
        Base.metadata.create_all(bind=engine)
        print("✅ 数据表创建成功")
        
        # 3. 创建向量索引
        print("🔍 创建向量索引...")
        try:
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_embedding 
                ON rewrite_records 
                USING ivfflat (embedding vector_cosine_ops)
                WITH (lists = 100)
            """))
            conn.commit()
            print("✅ 向量索引创建成功")
        except Exception as e:
            print(f"⚠️  向量索引创建失败（可能已存在）: {e}")
        
        # 4. 创建其他索引
        print("🔍 创建其他索引...")
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_created_at 
            ON rewrite_records (created_at)
        """))
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_user_id 
            ON rewrite_records (user_id)
        """))
        conn.commit()
        print("✅ 索引创建成功")
    
    print("🎉 数据库初始化完成！")

if __name__ == "__main__":
    init_database()
```

---

### 阶段 7：归档脚本（优先级：🟢 低）

#### 7.1 创建月度归档脚本

**新文件**: `backend/scripts/monthly_archive.py`

```python
#!/usr/bin/env python3
"""
月度归档脚本

功能：
1. 导出 30 天前的数据到 Parquet
2. Push 到 Hugging Face Datasets
3. 删除旧数据释放空间
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

import pandas as pd
import psycopg2
from datasets import Dataset
from huggingface_hub import HfApi

# 添加后端路径
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.core.config import settings

def archive_old_records(days: int = 30):
    """归档旧记录"""
    print(f"📦 开始归档 {days} 天前的数据...")
    
    # 1. 连接 Neon 数据库
    conn = psycopg2.connect(settings.database_url)
    
    # 2. 导出旧数据
    query = f"""
        SELECT id, user_id, source_text, result_text, 
               embedding::text, metadata, created_at
        FROM rewrite_records
        WHERE created_at < NOW() - INTERVAL '{days} days'
    """
    df = pd.read_sql(query, conn)
    
    if len(df) == 0:
        print("✅ 无数据需要归档")
        return
    
    print(f"📊 找到 {len(df)} 条记录需要归档")
    
    # 3. 保存为 Parquet
    month = (datetime.now() - timedelta(days=days)).strftime('%Y%m')
    filename = f"/tmp/archive_{month}.parquet"
    df.to_parquet(filename, compression='snappy')
    print(f"💾 已保存到 {filename}")
    
    # 4. Push 到 Hugging Face Datasets
    if os.getenv("HF_TOKEN"):
        print("🚀 上传到 Hugging Face Datasets...")
        api = HfApi()
        dataset_id = os.getenv("HF_DATASET_ID", "ai-rewrite-dataset")
        
        api.upload_file(
            path_or_fileobj=filename,
            path_in_repo=f"archive_{month}.parquet",
            repo_id=dataset_id,
            repo_type="dataset"
        )
        print(f"✅ 已上传到 {dataset_id}")
    else:
        print("⚠️  未配置 HF_TOKEN，跳过上传")
    
    # 5. 删除旧数据
    print("🗑️  删除旧数据...")
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM rewrite_records WHERE created_at < NOW() - INTERVAL '{days} days'")
    conn.commit()
    print(f"✅ 已删除 {cursor.rowcount} 条记录")
    
    conn.close()
    print("🎉 归档完成！")

if __name__ == "__main__":
    archive_old_records()
```

---

## 📊 成本估算

### 阶段 1：MVP（0-2 个月）

| 项目 | 用量 | 单价 | 月费 |
|------|------|------|------|
| **Neon PostgreSQL** | 512 MB | 免费 | ¥0 |
| **Hugging Face Spaces** | Docker 容器 | 免费 | ¥0 |
| **豆包 Embedding** | 1 万次/月 | ¥0.0007/千 tokens | ¥7 |
| **火山方舟 Claude API** | 1 万次/月 | 约¥0.01/次 | ¥100 |
| **Vercel 前端** | 静态托管 | 免费 | ¥0 |
| **合计** | - | - | **¥107/月** |

### 阶段 2：增长期（3-6 个月）

| 项目 | 用量 | 单价 | 月费 |
|------|------|------|------|
| **Neon Pro** | 8 GB | $30/月 | ¥216 |
| **豆包 Embedding** | 10 万次/月 | ¥0.0007/千 tokens | ¥70 |
| **火山方舟 Claude API** | 10 万次/月 | 约¥0.01/次 | ¥1000 |
| **合计** | - | - | **¥1286/月** |

---

## ✅ 验收标准

### 功能验收

- [ ] 向量检索正常（相似度>0.7 的记录能被检索到）
- [ ] RAG 提示词构建正确（包含相似示例）
- [ ] 改写结果质量提升（有示例 vs 无示例对比）
- [ ] 数据库连接稳定（无连接池耗尽问题）
- [ ] 归档脚本正常运行（每月自动执行）

### 性能验收

- [ ] 向量检索延迟 <50ms
- [ ] Embedding 生成延迟 <100ms
- [ ] 整体 API 响应时间 <3 秒
- [ ] 数据库连接池无泄漏

### 成本验收

- [ ] 首月成本 <¥200
- [ ] 数据库使用量 <400 MB（触发告警前）
- [ ] API 调用次数可监控

---

## 📞 下一步行动

**立即可执行**：
1. ✅ 创建 Neon 账号和项目
2. ✅ 更新数据库模型和配置
3. ✅ 运行数据库初始化脚本
4. ✅ 测试向量检索功能

**待用户确认**：
- [ ] 是否立即开始实施？
- [ ] 优先实施哪个阶段？
- [ ] 是否需要调整技术方案？

---

**文档版本**: v1.0  
**创建时间**: 2026-04-01  
**最后更新**: 2026-04-01  
**状态**: 待评审
