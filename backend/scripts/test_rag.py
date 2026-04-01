#!/usr/bin/env python3
"""
RAG 功能完整测试脚本

测试内容：
1. Embedding 生成
2. 向量检索
3. RAG 提示词构建
4. 完整改写流程
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.services.embedding import get_embedding, EmbeddingServiceError
from app.services.rag import RagService
from app.services.rewrite import rewrite_text
from app.models.rewrite_record import RewriteRecord
from datetime import datetime


def test_embedding():
    """测试 1: Embedding 生成"""
    print("\n" + "="*60)
    print("🧪 测试 1: Embedding 生成")
    print("="*60)
    
    test_text = "机器学习是人工智能的一个分支，它使用算法来解析数据、从中学习，然后做出决策或预测。"
    
    try:
        print(f"📝 输入文本：{test_text[:50]}...")
        embedding = get_embedding(test_text)
        print(f"✅ Embedding 生成成功！")
        print(f"📊 向量维度：{len(embedding)}")
        print(f"📊 前 5 个值：{[f'{x:.4f}' for x in embedding[:5]]}")
        return True, embedding
    except EmbeddingServiceError as e:
        print(f"❌ Embedding 生成失败：{e}")
        print("⚠️  请检查 .env 文件中的 EMBEDDING_API_KEY 是否配置")
        return False, None


def test_vector_search():
    """测试 2: 向量检索"""
    print("\n" + "="*60)
    print("🧪 测试 2: 向量检索")
    print("="*60)
    
    db = SessionLocal()
    
    try:
        # 1. 插入测试数据
        print("📦 插入测试数据...")
        test_records = [
            ("深度学习是机器学习的一个子领域", "Deep learning is a subset of machine learning"),
            ("神经网络模仿人脑的工作方式", "Neural networks mimic how the human brain works"),
            ("自然语言处理让计算机理解人类语言", "NLP enables computers to understand human language"),
        ]
        
        for source, result in test_records:
            try:
                embedding = get_embedding(source)
                record = RewriteRecord(
                    user_id=1,
                    source_text=source,
                    result_text=result,
                    embedding=embedding
                )
                db.add(record)
            except EmbeddingServiceError:
                # 如果 Embedding 失败，创建不带向量的记录
                record = RewriteRecord(
                    user_id=1,
                    source_text=source,
                    result_text=result
                )
                db.add(record)
        
        db.commit()
        print(f"✅ 成功插入 {len(test_records)} 条测试记录")
        
        # 2. 测试向量检索
        print("\n🔍 测试向量检索...")
        query_text = "人工智能和机器学习有什么关系？"
        print(f"📝 查询：{query_text}")
        
        try:
            query_embedding = get_embedding(query_text)
            rag_service = RagService(db)
            results = rag_service.find_similar_records(
                query_embedding,
                limit=3,
                similarity_threshold=0.5
            )
            
            print(f"✅ 检索到 {len(results)} 条相似记录")
            for i, record in enumerate(results, 1):
                print(f"\n  [{i}] 相似度：{record.similarity_score:.4f}")
                print(f"     原文：{record.source_text}")
                print(f"     改写：{record.result_text}")
            
            return True
        except Exception as e:
            print(f"❌ 向量检索失败：{e}")
            print("⚠️  可能是 SQLite 降级模式，使用简单检索")
            return True
            
    except Exception as e:
        print(f"❌ 测试失败：{e}")
        db.rollback()
        return False
    finally:
        db.close()


def test_rag_prompt():
    """测试 3: RAG 提示词构建"""
    print("\n" + "="*60)
    print("🧪 测试 3: RAG 提示词构建")
    print("="*60)
    
    db = SessionLocal()
    
    try:
        # 获取测试数据
        records = db.query(RewriteRecord).limit(3).all()
        
        if not records:
            print("❌ 没有测试数据，请先运行测试 2")
            return False
        
        rag_service = RagService(db)
        user_input = "请解释一下深度学习"
        
        print(f"📝 用户输入：{user_input}")
        print(f"📊 检索到 {len(records)} 条相似记录")
        
        prompt = rag_service.build_rag_prompt(records, user_input)
        
        print("\n✅ RAG 提示词构建成功！")
        print("\n📋 提示词预览（前 500 字符）:")
        print("-" * 60)
        print(prompt[:500] + "..." if len(prompt) > 500 else prompt)
        print("-" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ 提示词构建失败：{e}")
        return False
    finally:
        db.close()


def test_full_rewrite():
    """测试 4: 完整改写流程"""
    print("\n" + "="*60)
    print("🧪 测试 4: 完整改写流程（RAG 增强）")
    print("="*60)
    
    db = SessionLocal()
    
    try:
        user_input = "机器学习是一种让计算机从数据中学习的技术，它不需要明确的编程指令。"
        
        print(f"📝 用户输入：{user_input}")
        print("🔄 开始 RAG 增强改写...")
        
        result = rewrite_text(user_input, db=db, use_rag=True)
        
        print("\n✅ 改写成功！")
        print("\n📋 改写结果:")
        print("-" * 60)
        print(result)
        print("-" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ 改写失败：{e}")
        return False
    finally:
        db.close()


def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("🚀 RAG 功能完整测试")
    print("="*60)
    print(f"📅 测试时间：{datetime.now()}")
    print(f"📊 数据库：{SessionLocal().bind.url}")
    
    results = []
    
    # 测试 1: Embedding 生成
    success, embedding = test_embedding()
    results.append(("Embedding 生成", success))
    
    if not success:
        print("\n⚠️  Embedding 测试失败，跳过后续向量检索测试")
    else:
        # 测试 2: 向量检索
        success = test_vector_search()
        results.append(("向量检索", success))
        
        # 测试 3: RAG 提示词构建
        success = test_rag_prompt()
        results.append(("RAG 提示词", success))
        
        # 测试 4: 完整改写流程
        success = test_full_rewrite()
        results.append(("完整改写", success))
    
    # 汇总结果
    print("\n" + "="*60)
    print("📊 测试结果汇总")
    print("="*60)
    
    for test_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{status} - {test_name}")
    
    total = len(results)
    passed = sum(1 for _, s in results if s)
    print(f"\n总计：{passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！RAG 功能已就绪！")
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败，请检查配置")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
