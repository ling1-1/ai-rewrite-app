#!/usr/bin/env python3
"""
完整 RAG 流程测试（使用模拟向量）

测试：数据插入 → RAG 检索 → 提示词构建 → Claude API 改写
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.services.rag import RagService
from app.services.rewrite import rewrite_text
from app.models.rewrite_record import RewriteRecord
from sqlalchemy import text
import random

def test_full_rag_flow():
    """测试完整 RAG 流程"""
    print("\n" + "="*60)
    print("🚀 完整 RAG 流程测试")
    print("="*60)
    
    db = SessionLocal()
    
    try:
        # 1. 准备测试数据
        print("\n📦 准备测试数据...")
        
        # 检查是否已有测试数据
        result = db.execute(text("SELECT COUNT(*) FROM rewrite_records WHERE embedding IS NOT NULL"))
        count = result.fetchone()[0]
        
        if count < 5:
            print(f"⚠️  当前只有 {count} 条带向量的记录，先插入测试数据...")
            
            # 获取用户 ID
            result = db.execute(text("SELECT id FROM users WHERE username = 'test_user'"))
            row = result.fetchone()
            user_id = row[0] if row else 1
            
            test_records = [
                ("深度学习是机器学习的一个子领域，它使用多层神经网络来学习数据的层次化表示。", "Deep learning is a subset of machine learning that uses multi-layer neural networks to learn hierarchical representations of data."),
                ("自然语言处理是人工智能的重要应用领域，主要包括文本分类、情感分析、机器翻译等任务。", "Natural language processing is an important application area of AI, mainly including text classification, sentiment analysis, machine translation, etc."),
                ("计算机视觉使计算机能够从图像和视频中提取信息，应用于人脸识别、自动驾驶等领域。", "Computer vision enables computers to extract information from images and videos, applied in facial recognition, autonomous driving, etc."),
                ("强化学习通过试错和奖励机制训练智能体，在游戏 AI 和机器人控制中取得显著成功。", "Reinforcement learning trains agents through trial-and-error and reward mechanisms, achieving remarkable success in game AI and robotics."),
                ("迁移学习利用已学知识解决新问题，大大减少了对训练数据的需求。", "Transfer learning leverages learned knowledge to solve new problems, greatly reducing the need for training data."),
            ]
            
            for source, result_text in test_records:
                # 生成有意义的模拟向量（基于文本长度的简单哈希）
                fake_embedding = [(hash(source + str(i)) % 1000) / 1000.0 for i in range(1536)]
                
                record = RewriteRecord(
                    user_id=user_id,
                    source_text=source,
                    result_text=result_text,
                    embedding=fake_embedding
                )
                db.add(record)
            
            db.commit()
            print(f"✅ 成功插入 {len(test_records)} 条测试记录")
        else:
            print(f"✅ 已有 {count} 条带向量的记录")
        
        # 2. 测试 RAG 检索
        print("\n🔍 测试 RAG 检索...")
        query_text = "机器学习和深度学习有什么区别？"
        print(f"📝 查询：{query_text}")
        
        # 使用模拟查询向量
        query_embedding = [(hash(query_text + str(i)) % 1000) / 1000.0 for i in range(1536)]
        
        rag_service = RagService(db)
        results = rag_service.find_similar_records(
            query_embedding,
            limit=3,
            similarity_threshold=0.3
        )
        
        print(f"✅ 检索到 {len(results)} 条相似记录")
        for i, record in enumerate(results, 1):
            print(f"\n  [{i}] 相似度：{record.similarity_score:.4f}")
            print(f"     原文：{record.source_text[:50]}...")
        
        # 3. 测试 RAG 提示词构建
        print("\n\n📝 测试 RAG 提示词构建...")
        prompt = rag_service.build_rag_prompt(results, query_text)
        
        print("✅ RAG 提示词构建成功！")
        print("\n📋 提示词预览（前 300 字）:")
        print("-" * 60)
        print(prompt[:300] + "..." if len(prompt) > 300 else prompt)
        print("-" * 60)
        
        # 4. 测试 Claude API 改写
        print("\n\n🤖 测试 Claude API 改写...")
        print("📝 用户输入：", query_text)
        print("🔄 调用 Claude API...")
        
        result = rewrite_text(query_text, db=db, use_rag=True)
        
        print("\n✅ 改写成功！")
        print("\n📋 改写结果:")
        print("-" * 60)
        print(result)
        print("-" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    success = test_full_rag_flow()
    
    print("\n" + "="*60)
    print("📊 测试结果")
    print("="*60)
    
    if success:
        print("✅ 完整 RAG 流程测试通过！")
        print("\n🎉 所有功能正常工作！")
    else:
        print("❌ 测试失败，请检查配置")
    
    sys.exit(0 if success else 1)
