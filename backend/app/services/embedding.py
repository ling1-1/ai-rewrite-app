"""
豆包 Embedding 服务

用于将文本转换为 1536 维向量，支持 RAG 检索
"""

import httpx
from app.core.config import settings


class EmbeddingServiceError(Exception):
    """Embedding 服务异常"""
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
    """提取 API 错误消息"""
    try:
        payload = response.json()
    except ValueError:
        return response.text or f"HTTP {response.status_code}"
    
    error = payload.get("error", {})
    if isinstance(error, dict):
        return error.get("message") or error.get("type") or f"HTTP {response.status_code}"
    
    return str(error) or f"HTTP {response.status_code}"


# 测试函数
if __name__ == "__main__":
    # 测试 Embedding 服务
    test_text = "这是一个测试文本，用于验证 Embedding 服务是否正常工作。"
    try:
        embedding = get_embedding(test_text)
        print(f"✅ Embedding 生成成功！")
        print(f"📊 向量维度：{len(embedding)}")
        print(f"📊 前 5 个值：{embedding[:5]}")
    except EmbeddingServiceError as e:
        print(f"❌ Embedding 生成失败：{e}")
