#!/usr/bin/env python3
"""
火山 VikingDB 异步数据写入服务

实现批量异步写入，提高数据导入效率
"""

import asyncio
import aiohttp
import hashlib
import time
from typing import List, Dict, Optional
from datetime import datetime
import os

# 配置
AK = os.getenv("VOLC_AK", "")
SK = os.getenv("VOLC_SK", "")
REGION = os.getenv("VOLC_REGION", "cn-beijing")
COLLECTION_NAME = os.getenv("VIKING_COLLECTION", "ai_rewrite_kb")

# VikingDB API 端点
API_ENDPOINT = f"https://vikingdb.{REGION}.volces.com"


class VikingDBAsyncWriter:
    """VikingDB 异步写入器"""
    
    def __init__(self, ak: str = None, sk: str = None, region: str = None):
        """
        初始化
        
        Args:
            ak: Access Key ID
            sk: Secret Access Key
            region: 地域
        """
        self.ak = ak or AK
        self.sk = sk or SK
        self.region = region or REGION
        
        if not self.ak or not self.sk:
            raise ValueError("请配置 VOLC_AK 和 VOLC_SK 环境变量")
        
        self.collection_name = COLLECTION_NAME
        self.session: Optional[aiohttp.ClientSession] = None
        
        print(f"✅ VikingDB 异步写入器初始化成功")
        print(f"📍 区域：{self.region}")
        print(f"📦 数据集：{self.collection_name}")
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self.session:
            await self.session.close()
    
    def _generate_signature(self, method: str, path: str, body: dict) -> Dict[str, str]:
        """
        生成火山签名
        
        Args:
            method: HTTP 方法
            path: 请求路径
            body: 请求体
            
        Returns:
            签名字头
        """
        # 简化签名（生产环境需要完整签名算法）
        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        
        return {
            "X-Date": timestamp,
            "Content-Type": "application/json",
            "Authorization": f"AKSK {self.ak}:{self.sk}"  # 简化版
        }
    
    async def insert_single(self, data: Dict) -> Dict:
        """
        插入单条数据
        
        Args:
            data: 数据字典，包含：
                - original_text: 原文
                - rewrite_text: 改写结果
                - metadata: 元数据（可选）
                
        Returns:
            插入结果
        """
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        url = f"{API_ENDPOINT}/api/v1/collections/{self.collection_name}/upsert"
        
        payload = {
            "fields": {
                "original_text": data.get("original_text", ""),
                "rewrite_text": data.get("rewrite_text", ""),
                "metadata": data.get("metadata", {"source": "api"})
            }
        }
        
        headers = self._generate_signature("POST", url, payload)
        
        try:
            async with self.session.post(url, json=payload, headers=headers) as resp:
                result = await resp.json()
                
                if resp.status == 200:
                    print(f"✅ 插入成功：{data.get('original_text', '')[:50]}...")
                    return {"success": True, "data": result}
                else:
                    print(f"❌ 插入失败：{result}")
                    return {"success": False, "error": result}
        except Exception as e:
            print(f"❌ 请求异常：{e}")
            return {"success": False, "error": str(e)}
    
    async def insert_batch(self, documents: List[Dict], batch_size: int = 10) -> Dict:
        """
        批量插入数据
        
        Args:
            documents: 文档列表
            batch_size: 批次大小
            
        Returns:
            插入结果统计
        """
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        total = len(documents)
        success_count = 0
        failed_count = 0
        
        print(f"\n📦 开始批量插入 {total} 条数据...")
        start_time = time.time()
        
        # 分批处理
        for i in range(0, total, batch_size):
            batch = documents[i:i+batch_size]
            print(f"\n批次 {i//batch_size + 1}/{(total + batch_size - 1)//batch_size}")
            
            # 并发插入批次数据
            tasks = [self.insert_single(doc) for doc in batch]
            results = await asyncio.gather(*tasks)
            
            # 统计结果
            for result in results:
                if result.get("success"):
                    success_count += 1
                else:
                    failed_count += 1
            
            # 限流（避免过快）
            await asyncio.sleep(0.1)
        
        elapsed = time.time() - start_time
        
        print(f"\n{'='*60}")
        print(f"✅ 批量插入完成！")
        print(f"📊 总计：{total} 条")
        print(f"✅ 成功：{success_count} 条")
        print(f"❌ 失败：{failed_count} 条")
        print(f"⏱️  耗时：{elapsed:.2f} 秒")
        print(f"⚡ 速度：{total/elapsed:.2f} 条/秒")
        print(f"{'='*60}")
        
        return {
            "total": total,
            "success": success_count,
            "failed": failed_count,
            "elapsed": elapsed
        }
    
    async def search(self, query_text: str, limit: int = 5) -> List[Dict]:
        """
        文本检索
        
        Args:
            query_text: 查询文本
            limit: 返回数量
            
        Returns:
            检索结果
        """
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        url = f"{API_ENDPOINT}/api/v1/collections/{self.collection_name}/search"
        
        payload = {
            "text": query_text,
            "limit": limit,
            "dense_weight": 1.0
        }
        
        headers = self._generate_signature("POST", url, payload)
        
        try:
            async with self.session.post(url, json=payload, headers=headers) as resp:
                result = await resp.json()
                
                if resp.status == 200:
                    return result.get("data", [])
                else:
                    print(f"❌ 检索失败：{result}")
                    return []
        except Exception as e:
            print(f"❌ 请求异常：{e}")
            return []


async def test_async_writer():
    """测试异步写入器"""
    print("="*60)
    print("🚀 VikingDB 异步写入测试")
    print("="*60)
    
    # 测试数据
    test_docs = [
        {
            "original_text": "机器学习是人工智能的一个分支，它使用算法来解析数据、从中学习，然后做出决策或预测。",
            "rewrite_text": "Machine learning is a branch of artificial intelligence that uses algorithms to analyze data, learn from it, and make decisions or predictions.",
            "metadata": {"topic": "人工智能", "word_count": 50}
        },
        {
            "original_text": "深度学习是机器学习的一个子领域，它使用多层神经网络来学习数据的层次化表示。",
            "rewrite_text": "Deep learning is a subset of machine learning that uses multi-layer neural networks to learn hierarchical representations of data.",
            "metadata": {"topic": "深度学习", "word_count": 45}
        },
        {
            "original_text": "自然语言处理是人工智能的重要应用领域，主要包括文本分类、情感分析、机器翻译等任务。",
            "rewrite_text": "Natural language processing is an important application area of AI, mainly including text classification, sentiment analysis, machine translation, etc.",
            "metadata": {"topic": "自然语言处理", "word_count": 48}
        },
    ]
    
    async with VikingDBAsyncWriter() as writer:
        # 测试批量插入
        result = await writer.insert_batch(test_docs, batch_size=2)
        
        if result["success"] > 0:
            print("\n✅ 测试通过！")
            
            # 测试检索
            print("\n📝 测试检索...")
            results = await writer.search("机器学习是什么", limit=2)
            
            if results:
                print(f"\n✅ 检索到 {len(results)} 条结果:")
                for i, doc in enumerate(results, 1):
                    print(f"\n[{i}] 相似度：{doc.get('score', 'N/A')}")
                    fields = doc.get('fields', {})
                    print(f"    原文：{fields.get('original_text', 'N/A')[:100]}...")
                    print(f"    改写：{fields.get('rewrite_text', 'N/A')[:100]}...")
            else:
                print("\n⚠️  检索结果为空（可能是数据还在向量化中）")
        else:
            print("\n❌ 测试失败")


if __name__ == "__main__":
    asyncio.run(test_async_writer())
