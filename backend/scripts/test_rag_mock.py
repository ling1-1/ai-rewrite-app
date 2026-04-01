#!/usr/bin/env python3
"""
RAG 逻辑测试（不依赖真实 API）

使用模拟数据测试 RAG 检索和提示词构建逻辑
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.services.rag import RagService
from app.models.rewrite_record import RewriteRecord
from datetime import datetime
import random

def test_rag_logic():
    """测试 RAG 逻辑（使用模拟向量）"""
    print("\n" + "="*60)
    print("🧪 RAG 逻辑测试（模拟数据）")
    print("="*60)
    
    db = SessionLocal()
    
    try:
        # 1. 先创建测试用户（使用原始 SQL）
        print("📦 创建测试用户...")
        from sqlalchemy import text
        
        # 检查是否已存在
        result = db.execute(text("SELECT id FROM users WHERE username = 'test_user'"))
        row = result.fetchone()
        
        if row:
            user_id = row[0]
            print(f"✅ 测试用户已存在，ID: {user_id}")
        else:
            db.execute(text("""
                INSERT INTO users (username, email, password_hash) 
                VALUES ('test_user', 'test@example.com', 'hashed_password')
            """))
            db.commit()
            
            result = db.execute(text("SELECT id FROM users WHERE username = 'test_user'"))
            user_id = result.fetchone()[0]
            print(f"✅ 测试用户创建成功，ID: {user_id}")
        
        # 2. 插入测试数据（使用随机向量）
        print("\n📦 插入测试数据（模拟向量）...")
        test_records = [
            ("深度学习是机器学习的一个子领域", "Deep learning is a subset of machine learning"),
            ("神经网络模仿人脑的工作方式", "Neural networks mimic how the human brain works"),
            ("自然语言处理让计算机理解人类语言", "NLP enables computers to understand human language"),
            ("计算机视觉使机器能够看到和理解图像", "Computer vision enables machines to see and understand images"),
            ("强化学习通过奖励机制训练 AI 模型", "Reinforcement learning trains AI models through reward mechanisms"),
        ]
        
        for source, result in test_records:
            # 生成随机向量（模拟 Embedding）
            fake_embedding = [random.random() for _ in range(1536)]
            
            record = RewriteRecord(
                user_id=user_id,
                source_text=source,
                result_text=result,
                embedding=fake_embedding
            )
            db.add(record)
        
        db.commit()
        print(f"✅ 成功插入 {len(test_records)} 条测试记录")
        
        # 2. 测试 RAG 检索
        print("\n🔍 测试 RAG 检索...")
        query_text = "人工智能和机器学习有什么关系？"
        print(f"📝 查询：{query_text}")
        
        # 使用随机查询向量
        query_embedding = [random.random() for _ in range(1536)]
        
        rag_service = RagService(db)
        results = rag_service.find_similar_records(
            query_embedding,
            limit=3,
            similarity_threshold=0.3  # 降低阈值
        )
        
        print(f"✅ 检索到 {len(results)} 条相似记录")
        for i, record in enumerate(results, 1):
            print(f"\n  [{i}] 相似度：{record.similarity_score:.4f}")
            print(f"     原文：{record.source_text}")
            print(f"     改写：{record.result_text}")
        
        # 3. 测试 RAG 提示词构建
        print("\n\n📝 测试 RAG 提示词构建...")
        prompt = rag_service.build_rag_prompt(results, query_text)
        
        print("✅ RAG 提示词构建成功！")
        print("\n📋 提示词预览:")
        print("-" * 60)
        print(prompt[:800] + "..." if len(prompt) > 800 else prompt)
        print("-" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False
    finally:
        db.close()


def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("🚀 RAG 逻辑测试（不依赖 API）")
    print("="*60)
    print(f"📅 测试时间：{datetime.now()}")
    
    success = test_rag_logic()
    
    print("\n" + "="*60)
    print("📊 测试结果")
    print("="*60)
    
    if success:
        print("✅ RAG 逻辑测试通过！")
        print("\n🎉 检索和提示词构建功能正常！")
        print("⚠️  注意：这是基于模拟向量的测试，真实效果需要 API 支持")
    else:
        print("❌ RAG 逻辑测试失败")
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
