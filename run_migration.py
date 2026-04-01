#!/usr/bin/env python3
"""执行数据库迁移"""

import os
import sys
from sqlalchemy import create_engine, text

# 连接数据库
db_url = os.getenv('DATABASE_URL')
print(f"🔧 连接数据库：{db_url[:50]}...")

engine = create_engine(db_url)

with engine.connect() as conn:
    print("\n📝 执行迁移：添加历史记录字段...")
    
    # 添加 name 字段
    try:
        conn.execute(text("ALTER TABLE rewrite_records ADD COLUMN IF NOT EXISTS name VARCHAR(200)"))
        print("✅ 添加 name 字段")
    except Exception as e:
        print(f"⚠️  name 字段已存在")
    
    # 添加 is_favorite 字段
    try:
        conn.execute(text("ALTER TABLE rewrite_records ADD COLUMN IF NOT EXISTS is_favorite BOOLEAN DEFAULT false"))
        print("✅ 添加 is_favorite 字段")
    except Exception as e:
        print(f"⚠️  is_favorite 字段已存在")
    
    # 添加 notes 字段
    try:
        conn.execute(text("ALTER TABLE rewrite_records ADD COLUMN IF NOT EXISTS notes TEXT"))
        print("✅ 添加 notes 字段")
    except Exception as e:
        print(f"⚠️  notes 字段已存在")
    
    # 创建配置表
    try:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS configs (
                id SERIAL PRIMARY KEY,
                key VARCHAR(100) UNIQUE NOT NULL,
                value TEXT NOT NULL,
                description TEXT,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """))
        print("✅ 创建 configs 表")
    except Exception as e:
        print(f"⚠️  configs 表已存在")
    
    # 插入默认配置
    try:
        conn.execute(text("""
            INSERT INTO configs (key, value, description) VALUES
            ('rag_top_k', '3', 'RAG 检索相似记录数量（1-10）'),
            ('rag_similarity_threshold', '0.7', 'RAG 检索相似度阈值（0-1）'),
            ('enable_registration', 'true', '是否允许注册'),
            ('system_prompt', '你是论文改写助手。')
            ON CONFLICT (key) DO NOTHING
        """))
        print("✅ 插入默认配置")
    except Exception as e:
        print(f"⚠️  配置已存在")
    
    conn.commit()

print("\n" + "="*60)
print("✅ 数据库迁移完成！")
print("="*60)
