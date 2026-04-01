#!/usr/bin/env python3
"""测试中转站 API - OpenAI 兼容格式"""

import httpx

API_KEY = "sk-cc1452dd1695f22ef2cde3253d993dd5c76652308b9d3427004b46f5fcb1194f"
BASE_URL = "https://api.xxdlzs.top"

# OpenAI 兼容格式
url = f"{BASE_URL}/v1/embeddings"
payload = {
    "model": "doubao-embedding-lite",
    "input": ["测试文本"],  # OpenAI 格式需要数组
}
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "content-type": "application/json",
}

print("🔍 测试中转站 API (OpenAI 兼容格式)...")
print(f"URL: {url}")
print(f"Model: {payload['model']}")
print(f"Input: {payload['input']}")

try:
    response = httpx.post(url, json=payload, headers=headers, timeout=30.0)
    print(f"\n📊 HTTP 状态码：{response.status_code}")
    print(f"📊 Content-Type: {response.headers.get('content-type')}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ API 调用成功！")
        print(f"📊 响应数据：{data}")
        
        if "data" in data and len(data["data"]) > 0:
            embedding = data["data"][0]["embedding"]
            print(f"✅ Embedding 维度：{len(embedding)}")
            print(f"✅ 前 5 个值：{embedding[:5]}")
        else:
            print("❌ 响应格式不正确")
    else:
        print(f"❌ HTTP 错误：{response.status_code}")
        print(f"响应内容：{response.text[:500]}")
        
except Exception as e:
    print(f"❌ 请求失败：{e}")
