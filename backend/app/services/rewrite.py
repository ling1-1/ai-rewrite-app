import httpx
from typing import Optional
from sqlalchemy.orm import Session

from app.core.config import settings
from app.services.embedding import get_embedding, EmbeddingServiceError
from app.services.rag import RagService


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
        raise RewriteServiceError("尚未配置 Anthropic API Key，请先在 backend/.env 中填写。")

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
        "x-api-key": settings.anthropic_api_key,
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
        raise RewriteServiceError("无法连接 Claude API，请检查网络或接口配置。") from exc

    data = response.json()
    content = data.get("content", [])
    result = "\n".join(
        item.get("text", "").strip()
        for item in content
        if item.get("type") == "text" and item.get("text")
    ).strip()

    if not result:
        raise RewriteServiceError("Claude API 已返回响应，但没有解析到可用文本。")

    return result


def _extract_error_message(response: httpx.Response) -> str:
    try:
        payload = response.json()
    except ValueError:
        return response.text or f"HTTP {response.status_code}"

    error = payload.get("error", {})
    if isinstance(error, dict):
        return error.get("message") or error.get("type") or f"HTTP {response.status_code}"

    return str(error) or f"HTTP {response.status_code}"
