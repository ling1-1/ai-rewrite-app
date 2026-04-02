#!/usr/bin/env python3
"""创建管理员账号和测试数据"""

from sqlalchemy import create_engine, text
from datetime import datetime, timedelta

# 数据库连接
engine = create_engine(
    "postgresql://neondb_owner:npg_JFMyeh5aIOn8@ep-ancient-moon-a1mkllm1-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"
)

with engine.connect() as conn:
    # 1. 创建管理员账号（用户名：admin，密码：admin123456）
    print("🔧 创建管理员账号...")
    conn.execute(text("""
        INSERT INTO users (username, password_hash, is_admin) 
        VALUES ('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzS3MebAJu', TRUE)
        ON CONFLICT (username) DO NOTHING
    """))
    conn.commit()
    print("✅ 管理员账号已创建（admin / admin123456）")

    # 2. 获取管理员 ID
    result = conn.execute(text("SELECT id FROM users WHERE username = 'admin'"))
    admin_id = result.scalar()
    print(f"📊 管理员 ID: {admin_id}")

    # 3. 插入测试历史记录
    print("\n🔧 插入测试历史记录...")
    
    test_records = [
        {
            "source": "机器学习是人工智能的一个分支，它使用统计技术使计算机系统能够从数据中学习并改进性能，而无需进行明确的编程。",
            "result": "机器学习作为人工智能的重要分支领域，通过运用统计学方法和技术手段，赋予计算机系统从数据中自主学习和持续优化性能的能力，无需依赖传统的人工编程方式。"
        },
        {
            "source": "深度学习是机器学习的一个子领域，它基于人工神经网络，特别是包含多个隐藏层的深层神经网络。",
            "result": "作为机器学习的重要子领域，深度学习以人工神经网络为基础架构，尤其侧重于具有多层隐藏层的深层神经网络结构的研究与应用。"
        },
        {
            "source": "自然语言处理（NLP）是人工智能和语言学领域的交叉学科，致力于使计算机能够理解、解释和生成人类语言。",
            "result": "自然语言处理（NLP）作为人工智能与语言学的交叉学科领域，其核心目标是赋予计算机理解、解析和生成人类自然语言的能力。"
        },
        {
            "source": "卷积神经网络（CNN）是一种专门用于处理网格状拓扑数据的深度学习架构，在图像识别领域取得了巨大成功。",
            "result": "卷积神经网络（CNN）作为一种专门针对网格状拓扑结构数据设计的深度学习架构，在图像识别与计算机视觉领域取得了显著成就和广泛应用。"
        },
        {
            "source": "强化学习是一种机器学习方法，通过与环境交互并接收奖励或惩罚信号来学习最优策略。",
            "result": "强化学习作为一种机器学习范式，通过与环境的持续交互作用，并基于奖励或惩罚反馈信号的学习机制，逐步优化并习得最优决策策略。"
        }
    ]
    
    for i, record in enumerate(test_records, 1):
        conn.execute(text("""
            INSERT INTO rewrite_records 
            (user_id, name, source_text, result_text, model_used, is_favorite, notes, created_at, updated_at)
            VALUES 
            (:user_id, :name, :source_text, :result_text, :model_used, :is_favorite, :notes, :created_at, :updated_at)
        """), {
            "user_id": admin_id,
            "name": f"测试记录 {i}",
            "source_text": record["source"],
            "result_text": record["result"],
            "model_used": "doubao-lite-4k-241215",
            "is_favorite": i % 2 == 0,  # 偶数记录收藏
            "notes": f"这是第 {i} 条测试数据",
            "created_at": datetime.now() - timedelta(days=5-i),
            "updated_at": datetime.now()
        })
    
    conn.commit()
    print(f"✅ 已插入 {len(test_records)} 条测试历史记录")

    # 4. 验证
    print("\n📊 验证数据...")
    result = conn.execute(text("""
        SELECT u.username, u.is_admin, COUNT(r.id) as record_count
        FROM users u
        LEFT JOIN rewrite_records r ON u.id = r.user_id
        WHERE u.is_admin = TRUE
        GROUP BY u.id, u.username, u.is_admin
    """))
    for row in result:
        print(f"  管理员：{row[0]}, 收藏记录数：{row[2]}")

    result = conn.execute(text("SELECT COUNT(*) FROM rewrite_records"))
    total = result.scalar()
    print(f"  总历史记录数：{total}")

print("\n✅ 数据库初始化完成！")
print("\n📝 测试账号信息:")
print("  用户名：admin")
print("  密码：admin123456")
print("  权限：管理员")
