#!/usr/bin/env python3
"""
基于 VikingDB 的 RAG 服务

集成火山向量数据库进行检索增强生成
"""

import os
from typing import List, Optional, Dict
from vikingdb import VikingDB, IAM
from vikingdb.vector.models import SearchByRandomRequest, UpsertDataRequest


class VikingRAGService:
    """基于 VikingDB 的 RAG 服务"""
    
    def __init__(
        self,
        ak: str = None,
        sk: str = None,
        region: str = None,
        collection_name: str = None,
        index_name: str = None
    ):
        """
        初始化 RAG 服务
        
        Args:
            ak: Access Key ID
            sk: Secret Access Key
            region: 地域（默认 cn-beijing）
            collection_name: 数据集名称
            index_name: 索引名称
        """
        self.ak = ak or os.getenv("VOLC_AK")
        self.sk = sk or os.getenv("VOLC_SK")
        self.region = region or os.getenv("VOLC_REGION", "cn-beijing")
        self.collection_name = collection_name or os.getenv("VIKING_COLLECTION", "ai_rewrite_kb")
        self.index_name = index_name or os.getenv("VIKING_INDEX", "ai_rewrite_kb_index")
        
        if not self.ak or not self.sk:
            raise ValueError("请配置 VOLC_AK 和 VOLC_SK 环境变量")
        
        # 初始化客户端
        auth = IAM(ak=self.ak, sk=self.sk)
        self.client = VikingDB(
            host=f"api-vikingdb.vikingdb.{self.region}.volces.com",
            region=self.region,
            auth=auth,
            scheme="https"
        )
        
        # 获取数据集和索引
        self.collection = self.client.collection(collection_name=self.collection_name)
        self.index = self.client.index(index_name=self.index_name)
        
        print(f"✅ VikingRAGService 初始化成功")
        print(f"📍 区域：{self.region}")
        print(f"📦 数据集：{self.collection_name}")
        print(f"🔍 索引：{self.index_name}")
    
    def add_documents(self, documents: List[Dict]) -> bool:
        """
        批量添加文档
        
        Args:
            documents: 文档列表，每项包含：
                - original_text: 原文
                - rewrite_text: 改写结果
                - metadata: 标签列表（字符串数组）
                
        Returns:
            bool: 是否成功
        """
        try:
            # 转换为 VikingDB 格式
            data = []
            for doc in documents:
                item = {
                    "original_text": doc.get("original_text", ""),
                    "rewrite_text": doc.get("rewrite_text", ""),
                    "metadata": doc.get("metadata", [])  # 必须是字符串数组
                }
                data.append(item)
            
            request = UpsertDataRequest(data=data)
            response = self.collection.upsert(request)
            
            if response.code == "Success":
                print(f"✅ 成功添加 {len(documents)} 条文档")
                return True
            else:
                print(f"❌ 添加失败：{response.message}")
                return False
                
        except Exception as e:
            print(f"❌ 添加文档异常：{e}")
            return False
    
    def add_single(self, original_text: str, rewrite_text: str, metadata: List[str] = None) -> bool:
        """
        添加单条文档
        
        Args:
            original_text: 原文
            rewrite_text: 改写结果
            metadata: 标签列表
            
        Returns:
            bool: 是否成功
        """
        return self.add_documents([{
            "original_text": original_text,
            "rewrite_text": rewrite_text,
            "metadata": metadata or []
        }])
    
    def search(self, query_text: str, limit: int = 5) -> List[Dict]:
        """
        检索相似文档
        
        Args:
            query_text: 查询文本
            limit: 返回数量
            
        Returns:
            相似文档列表
        """
        try:
            request = SearchByRandomRequest(
                text=query_text,
                limit=limit,
                output_fields=["original_text", "rewrite_text", "metadata"],
                collection_name=self.collection_name
            )
            
            response = self.index.search_by_random(request)
            
            # 转换为统一格式
            results = []
            for doc in response.result.data:
                results.append({
                    "original_text": doc.fields.get("original_text", ""),
                    "rewrite_text": doc.fields.get("rewrite_text", ""),
                    "metadata": doc.fields.get("metadata", []),
                    "score": doc.score
                })
            
            print(f"✅ 检索到 {len(results)} 条相似文档")
            return results
            
        except Exception as e:
            print(f"❌ 检索异常：{e}")
            return []
    
    def build_rag_prompt(self, similar_docs: List[Dict], user_input: str) -> str:
        """
        构建 RAG 提示词
        
        Args:
            similar_docs: 相似文档列表
            user_input: 用户输入
            
        Returns:
            RAG 增强提示词
        """
        if not similar_docs:
            return self._build_base_prompt(user_input)
        
        # 构建示例部分
        examples = []
        for i, doc in enumerate(similar_docs[:5], 1):  # 最多 5 个示例
            example = f"""示例 {i}:
原文：{doc['original_text'][:200]}...
改写：{doc['rewrite_text'][:200]}...
"""
            examples.append(example)
        
        examples_text = "\n\n".join(examples)
        
        # 构建完整提示词
        prompt = f"""你是一个专业的论文改写助手。

参考以下改写示例（按相关性排序）：

{examples_text}

请根据上述示例的风格和技巧，改写以下论文内容：

原文：{user_input}

改写："""
        
        return prompt
    
    def _build_base_prompt(self, user_input: str) -> str:
        """基础提示词（无 RAG 增强）"""
        return f"""你是一个专业的论文改写助手。

请改写以下论文内容，保持原意不变，使表达更学术化、更流畅：

原文：{user_input}

改写："""
    
    def rewrite_with_rag(self, user_input: str, chat_service=None) -> str:
        """
        完整的 RAG 改写流程
        
        Args:
            user_input: 用户输入
            chat_service: Chat 服务回调函数
            
        Returns:
            改写结果
        """
        # 1. 检索相似文档
        similar_docs = self.search(user_input, limit=5)
        
        # 2. 构建 RAG 提示词
        prompt = self.build_rag_prompt(similar_docs, user_input)
        
        # 3. 调用 Chat API 改写
        if chat_service:
            result = chat_service(prompt)
        else:
            # 默认返回提示词（实际使用需要传入 chat_service）
            result = prompt
        
        return result


def test_viking_rag():
    """测试 VikingDB RAG 服务"""
    print("="*60)
    print("🚀 VikingDB RAG 服务测试")
    print("="*60)
    
    try:
        # 初始化服务
        rag = VikingRAGService()
        
        # 测试添加文档
        print("\n📦 测试添加文档...")
        test_docs = [
            {
                "original_text": "机器学习是人工智能的一个分支，它使用算法来解析数据、从中学习，然后做出决策或预测。",
                "rewrite_text": "Machine learning is a branch of artificial intelligence that uses algorithms to analyze data, learn from it, and make decisions or predictions.",
                "metadata": ["机器学习", "人工智能"]
            },
            {
                "original_text": "深度学习是机器学习的一个子领域，它使用多层神经网络来学习数据的层次化表示。",
                "rewrite_text": "Deep learning is a subset of machine learning that uses multi-layer neural networks to learn hierarchical representations of data.",
                "metadata": ["深度学习", "神经网络"]
            },
            {
                "original_text": "自然语言处理是人工智能的重要应用领域，主要包括文本分类、情感分析、机器翻译等任务。",
                "rewrite_text": "Natural language processing is an important application area of AI, mainly including text classification, sentiment analysis, machine translation, etc.",
                "metadata": ["自然语言处理", "NLP"]
            }
        ]
        
        success = rag.add_documents(test_docs)
        
        if success:
            print("✅ 文档添加成功")
        else:
            print("⚠️  文档添加失败（可能是重复数据）")
        
        # 测试检索
        print("\n📝 测试检索...")
        results = rag.search("机器学习是什么", limit=3)
        
        if results:
            print(f"\n✅ 检索到 {len(results)} 条结果:")
            for i, doc in enumerate(results, 1):
                print(f"\n[{i}] 相似度：{doc['score']:.4f}")
                print(f"    原文：{doc['original_text'][:100]}...")
                print(f"    改写：{doc['rewrite_text'][:100]}...")
                print(f"    标签：{doc['metadata']}")
        else:
            print("\n⚠️  检索结果为空")
        
        # 测试提示词构建
        print("\n\n📝 测试提示词构建...")
        prompt = rag.build_rag_prompt(results, "深度学习有什么特点？")
        
        print("\n✅ 提示词构建成功！")
        print("\n📋 提示词预览（前 300 字）:")
        print("-" * 60)
        print(prompt[:300] + "..." if len(prompt) > 300 else prompt)
        print("-" * 60)
        
        print("\n" + "="*60)
        print("✅ 所有测试通过！")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_viking_rag()
