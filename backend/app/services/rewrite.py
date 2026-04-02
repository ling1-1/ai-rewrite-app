import httpx
from typing import Optional
from sqlalchemy.orm import Session

from app.core.config import settings


class RewriteServiceError(Exception):
    pass


# 默认系统提示词（如果数据库中没有配置）
DEFAULT_SYSTEM_PROMPT = """
你是"JS 论文工作室"的论文改写助手。

你的任务是将用户输入的中文论文内容进行学术化改写和表达优化，但必须遵守以下规则：
1. 保持原意、事实、结论和逻辑结构不变。
2. 优先改写句式、连接方式和表述节奏，使表达更自然、更像人工撰写的论文文本。
3. 保留专业术语、专有名词、数据、年份、引用标记和关键概念，不要凭空增删。
4. 输出应偏向正式、清晰、流畅的中文书面学术表达。
5. 不要附加解释、分析、标题、备注、项目符号或引号。
6. 只返回改写后的正文内容。
""".strip()


def build_rag_prompt(similar_docs: list[dict], user_input: str) -> str:
    """根据检索结果构建统一的 RAG 提示词。"""
    if not similar_docs:
        return user_input

    examples = []
    for i, doc in enumerate(similar_docs[:5], 1):
        example = f"""示例 {i}:
原文：{doc.get('original_text', '')[:200]}...
改写：{doc.get('rewrite_text', '')[:200]}...
"""
        examples.append(example)

    examples_text = "\n\n".join(examples)
    return f"""你是一个专业的论文改写助手。

参考以下改写示例（按相关性排序）：

{examples_text}

请根据上述示例的风格和技巧，改写以下论文内容：

原文：{user_input}

改写："""


def rewrite_text(
    source_text: str,
    db: Optional[Session] = None,
    use_rag: bool = True
) -> str:
    """
    改写文本（支持 RAG 增强）
    
    Args:
        source_text: 原文
        db: 数据库会话（用于获取配置）
        use_rag: 是否启用 RAG 增强
        
    Returns:
        str: 改写后的文本
    """
    # 1. 获取系统提示词（从数据库配置）
    system_prompt = DEFAULT_SYSTEM_PROMPT
    model_name = settings.anthropic_model
    if db:
        try:
            from app.services.config_service import ConfigService
            config_service = ConfigService(db)
            system_prompt = config_service.get_system_prompt() or DEFAULT_SYSTEM_PROMPT
            model_name = config_service.get_rewrite_model(settings.anthropic_model)
        except Exception as e:
            print(f"⚠️  获取系统提示词失败：{e}")
    
    # 2. RAG 检索（如果启用）
    prompt = source_text
    if use_rag:
        try:
            # 获取 RAG 配置
            from app.services.config_service import ConfigService
            from app.services.vector_db_backend import get_vector_db
            
            config_service = ConfigService(db) if db else None
            rag_config = config_service.get_rag_config() if config_service else {'top_k': 3, 'similarity_threshold': 0.7}
            
            print(f"\n{'='*60}")
            print(f"🔍 RAG 检索启动")
            print(f"  查询：{source_text[:50]}...")
            print(f"  top_k: {rag_config['top_k']}")
            print(f"  相似度阈值：{rag_config['similarity_threshold']}")
            print(f"{'='*60}\n")
            
            # 使用向量数据库抽象层检索
            vector_db = get_vector_db()
            similar_docs = vector_db.search(source_text, limit=rag_config['top_k'])
            
            print(f"📚 检索到 {len(similar_docs)} 条相似记录:\n")
            for i, doc in enumerate(similar_docs, 1):
                print(f"[{i}] 相似度：{doc.get('score', 0):.4f}")
                print(f"    原文：{doc.get('original_text', '')[:80]}...")
                print(f"    改写：{doc.get('rewrite_text', '')[:80]}...")
                print()
            
            # 构建 RAG 提示词
            if similar_docs:
                prompt = build_rag_prompt(similar_docs, source_text)
                
                print(f"📝 构建的完整提示词:\n{'-'*60}")
                print(prompt)
                print(f"{'-'*60}\n")
            else:
                print(f"⚠️  未检索到相似记录，使用基础提示词\n")
                
        except Exception as e:
            print(f"⚠️  RAG 检索失败，使用基础提示词：{e}\n")
            import traceback
            traceback.print_exc()
            pass
    
    # 3. 调用 Chat API
    if not settings.anthropic_api_key:
        raise RewriteServiceError("尚未配置 API Key")

    # 构建正确的 URL（避免重复 /v1）
    base_url = settings.anthropic_base_url.rstrip('/')
    if base_url.endswith('/v3'):
        url = f"{base_url}/chat/completions"
    else:
        url = f"{base_url}/v1/chat/completions"
    
    payload = {
        "model": model_name,
        "max_tokens": settings.anthropic_max_tokens,
        "temperature": settings.anthropic_temperature,
        "messages": [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": prompt,
            }
        ],
    }
    headers = {
        "Authorization": f"Bearer {settings.anthropic_api_key}",
        "content-type": "application/json",
    }

    try:
        response = httpx.post(url, json=payload, headers=headers, timeout=90.0)
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        message = _extract_error_message(exc.response)
        raise RewriteServiceError(f"API 请求失败：{message}") from exc
    except httpx.HTTPError as exc:
        raise RewriteServiceError("无法连接 API，请检查网络或接口配置。") from exc

    # 调试：打印原始响应
    import json
    print(f"📊 API 原始响应：{json.dumps(response.json(), indent=2, ensure_ascii=False)[:500]}")
    
    data = response.json()
    
    # DeepSeek 格式响应
    if "choices" in data and len(data["choices"]) > 0:
        result = data["choices"][0]["message"]["content"].strip()
    # Anthropic/Claude 格式响应
    elif "content" in data:
        content = data.get("content", [])
        result = "\n".join(
            item.get("text", "").strip()
            for item in content
            if item.get("type") == "text" and item.get("text")
        ).strip()
    else:
        result = ""

    if not result:
        raise RewriteServiceError("API 已返回响应，但没有解析到可用文本。")

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
