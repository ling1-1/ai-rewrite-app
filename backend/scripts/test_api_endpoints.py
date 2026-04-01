#!/usr/bin/env python3
"""测试 API 连接 - 尝试不同端点"""

import httpx

API_KEY = "sk-cc1452dd1695f22ef2cde3253d993dd5c76652308b9d3427004b46f5fcb1194f"
BASE_URL = "https://api.xxdlzs.top"

test_text = "测试文本"

# 尝试不同的端点
endpoints = [
    "/v1/embeddings",
    "/embeddings",
    "/api/embeddings",
    "/api/v1/embeddings",
]

for endpoint in endpoints:
    url = f"{BASE_URL}{endpoint}"
    payload = {
        "model": "doubao-embedding-lite",
        "input": test_text,
    }
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "content-type": "application/json",
    }
    
    print(f"\n🔍 测试端点：{url}")
    try:
        response = httpx.post(url, json=payload, headers=headers, timeout=30.0)
        print(f"  状态码：{response.status_code}")
        print(f"  Content-Type: {response.headers.get('content-type', 'unknown')}")
        
        if response.status_code == 200 and 'application/json' in response.headers.get('content-type', ''):
            data = response.json()
            print(f"  ✅ 成功！")
            print(f"  数据：{data}")
            break
        else:
            print(f"  ❌ 失败：{response.text[:200]}")
    except Exception as e:
        print(f"  ❌ 错误：{e}")
