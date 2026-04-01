#!/usr/bin/env python3
"""
使用火山方舟 Doubao-embedding-vision 生成向量

接入点 ID: ep-20260315142813-689hq
模型：doubao-embedding-vision-250615
"""

import httpx
import json

# 配置
API_KEY = "d78c3528-7a65-4746-a704-43660d80493d"
ENDPOINT_ID = "ep-20260315142813-689hq"
BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"

def get_embedding(text: str):
    """
    获取文本的向量嵌入
    
    Args:
        text: 输入文本
        
    Returns:
        list: 向量（1536 维）
    """
    # 火山方舟 Embedding API 格式
    url = f"{BASE_URL}/embeddings"
    
    payload = {
        "model": ENDPOINT_ID,  # 使用接入点 ID
        "input": [text],  # 注意：需要是数组格式
    }
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    
    print(f"🔍 请求 URL: {url}")
    print(f"📝 输入文本：{text}")
    print(f"📦 请求体：{json.dumps(payload, ensure_ascii=False)}")
    
    try:
        response = httpx.post(url, json=payload, headers=headers, timeout=30.0)
        response.raise_for_status()
        
        result = response.json()
        print(f"✅ 响应：{json.dumps(result, ensure_ascii=False, indent=2)[:500]}")
        
        # 解析响应
        if "data" in result and len(result["data"]) > 0:
            embedding = result["data"][0]["embedding"]
            print(f"✅ 向量维度：{len(embedding)}")
            print(f"✅ 前 10 个值：{embedding[:10]}")
            return embedding
        else:
            print(f"❌ 响应格式错误：{result}")
            return None
            
    except httpx.HTTPStatusError as e:
        print(f"❌ HTTP 错误：{e}")
        print(f"响应内容：{e.response.text}")
        return None
    except Exception as e:
        print(f"❌ 请求失败：{e}")
        return None


if __name__ == "__main__":
    # 测试
    test_texts = [
        "机器学习是人工智能的一个分支",
        "深度学习使用神经网络学习数据表示",
        "自然语言处理让计算机理解人类语言",
    ]
    
    print("="*60)
    print("🚀 火山方舟 Embedding 测试")
    print("="*60)
    
    for text in test_texts:
        print(f"\n{'='*60}")
        embedding = get_embedding(text)
        if embedding:
            print(f"✅ 成功！向量长度：{len(embedding)}")
        print()
