#!/usr/bin/env python3
"""测试 API - OpenAI 兼容格式"""

import httpx

API_KEY = "sk-cc1452dd1695f22ef2cde3253d993dd5c76652308b9d3427004b46f5fcb1194f"
BASE_URL = "https://api.xxdlzs.top"

# 尝试 OpenAI 兼容格式
url = f"{BASE_URL}/v1/embeddings"
payload = {
    "model": "doubao-embedding-lite",
    "input": [test_text],  # 尝试数组格式
}
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "content-type": "application/json",
}

print(f"🔍 测试 OpenAI 兼容格式...")
print(f"URL: {url}")
print(f"Payload: {payload}")

try:
    response = httpx.post(url, json=payload, headers=headers, timeout=30.0)
    print(f"状态码：{response.status_code}")
    print(f"Content-Type: {response.headers.get('content-type')}")
    print(f"响应：{response.text[:500]}")
except Exception as e:
    print(f"错误：{e}")
