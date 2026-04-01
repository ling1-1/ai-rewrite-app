#!/usr/bin/env python3
"""测试 API 连接"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import httpx

API_KEY = "sk-cc1452dd1695f22ef2cde3253d993dd5c76652308b9d3427004b46f5fcb1194f"
BASE_URL = "https://api.xxdlzs.top"

print("🔍 测试 Embedding API...")

url = f"{BASE_URL}/embeddings"
payload = {
    "model": "doubao-embedding-lite",
    "input": "测试文本",
}
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "content-type": "application/json",
}

try:
    response = httpx.post(url, json=payload, headers=headers, timeout=30.0)
    print(f"📊 HTTP 状态码：{response.status_code}")
    print(f"📊 响应头：{dict(response.headers)}")
    print(f"📊 响应内容：{response.text[:500]}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ API 调用成功！")
        print(f"📊 数据：{data}")
    else:
        print(f"❌ API 调用失败：HTTP {response.status_code}")
        
except Exception as e:
    print(f"❌ 请求失败：{e}")
