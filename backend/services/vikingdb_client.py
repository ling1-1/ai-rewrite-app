#!/usr/bin/env python3
"""
火山 VikingDB 向量数据库对接

文档：https://www.volcengine.com/docs/84313/1817051
"""

from volcengine.vikingdb import VikingDBService
from volcengine.vikingdb import Collection
import os

# 配置（从环境变量读取）
AK = os.getenv("VOLC_AK", "")
SK = os.getenv("VOLC_SK", "")
REGION = os.getenv("VOLC_REGION", "cn-beijing")
COLLECTION_NAME = os.getenv("VIKING_COLLECTION", "ai-rewrite-kb")

# 从截图看，你用的是 doubao-embedding-vision-version-251215（2048 维）
EMBEDDING_MODEL = os.getenv("VIKING_EMBEDDING_MODEL", "doubao-embedding-vision-version-251215")


class VikingDBClient:
    """VikingDB 客户端"""
    
    def __init__(self, ak=None, sk=None, region=None):
        """
        初始化客户端
        
        Args:
            ak: Access Key ID
            sk: Secret Access Key
            region: 地域（默认 cn-beijing）
        """
        self.ak = ak or AK
        self.sk = sk or SK
        self.region = region or REGION
        
        if not self.ak or not self.sk:
            raise ValueError("请配置 VOLC_AK 和 VOLC_SK 环境变量")
        
        # 创建服务实例
        self.service = VikingDBService(
            ak=self.ak,
            sk=self.sk,
            region=self.region
        )
        
        print(f"✅ VikingDB 客户端初始化成功（区域：{self.region}）")
    
    def get_collection(self, name=None) -> Collection:
        """
        获取数据集
        
        Args:
            name: 数据集名称
            
        Returns:
            Collection 对象
        """
        collection_name = name or COLLECTION_NAME
        try:
            collection = self.service.get_collection(collection_name)
            print(f"✅ 获取数据集成功：{collection_name}")
            return collection
        except Exception as e:
            print(f"❌ 获取数据集失败：{e}")
            print(f"💡 请先在控制台创建数据集：{collection_name}")
            return None
    
    def search(self, query_text: str, limit: int = 5):
        """
        文本检索（自动向量化）
        
        Args:
            query_text: 查询文本
            limit: 返回数量
            
        Returns:
            相似的文档列表
        """
        collection = self.get_collection()
        if not collection:
            return []
        
        try:
            # VikingDB 支持直接文本检索（自动向量化）
            results = collection.search(
                text=query_text,
                limit=limit,
                dense_weight=1.0  # 稠密向量权重
            )
            
            print(f"✅ 检索成功，返回 {len(results)} 条结果")
            return results
        except Exception as e:
            print(f"❌ 检索失败：{e}")
            return []
    
    def add_documents(self, documents: list):
        """
        添加文档
        
        Args:
            documents: 文档列表，每项包含：
                - text: 文本内容
                - metadata: 元数据（可选）
                
        Returns:
            添加结果
        """
        collection = self.get_collection()
        if not collection:
            return False
        
        try:
            # 批量写入（自动向量化）
            result = collection.upsert_fields(documents)
            print(f"✅ 成功添加 {len(documents)} 条文档")
            return result
        except Exception as e:
            print(f"❌ 添加文档失败：{e}")
            return False


def test_vikingdb():
    """测试 VikingDB 连接"""
    print("="*60)
    print("🚀 VikingDB 连接测试")
    print("="*60)
    
    try:
        client = VikingDBClient()
        
        # 测试检索
        print("\n📝 测试检索...")
        results = client.search("机器学习是什么", limit=3)
        
        if results:
            print(f"\n✅ 检索到 {len(results)} 条结果:")
            for i, doc in enumerate(results, 1):
                print(f"\n[{i}] 相似度：{doc.get('score', 'N/A')}")
                print(f"    内容：{doc.get('fields', {}).get('text', 'N/A')[:100]}...")
        else:
            print("\n⚠️  检索结果为空（可能是数据集还没有数据）")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败：{e}")
        print("\n💡 请检查:")
        print("1. Access Key 和 Secret Key 是否正确")
        print("2. 数据集是否已创建")
        print("3. 地域配置是否正确")
        return False


if __name__ == "__main__":
    test_vikingdb()
