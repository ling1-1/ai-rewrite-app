#!/usr/bin/env python3
"""添加 embedding 列到 rewrite_records 表"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from sqlalchemy import text
from app.db.session import engine

print("🔧 开始更新数据库结构...")

with engine.connect() as conn:
    # 检查 embedding 列是否存在
    result = conn.execute(text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'rewrite_records' AND column_name = 'embedding'
    """))
    
    if result.fetchone():
        print("✅ embedding 列已存在，跳过")
    else:
        print("📦 添加 embedding 列...")
        conn.execute(text("""
            ALTER TABLE rewrite_records 
            ADD COLUMN embedding vector(1536)
        """))
        conn.commit()
        print("✅ embedding 列添加成功")
    
    # 检查 updated_at 列
    result = conn.execute(text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'rewrite_records' AND column_name = 'updated_at'
    """))
    
    if result.fetchone():
        print("✅ updated_at 列已存在，跳过")
    else:
        print("📦 添加 updated_at 列...")
        conn.execute(text("""
            ALTER TABLE rewrite_records 
            ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        """))
        conn.commit()
        print("✅ updated_at 列添加成功")
    
    # 创建向量索引
    print("🔍 创建向量索引...")
    try:
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_embedding 
            ON rewrite_records 
            USING ivfflat (embedding vector_cosine_ops)
            WITH (lists = 100)
        """))
        conn.commit()
        print("✅ 向量索引创建成功")
    except Exception as e:
        print(f"⚠️  索引创建警告：{e}")
    
    # 创建 updated_at 索引
    print("🔍 创建 updated_at 索引...")
    try:
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_updated_at 
            ON rewrite_records (updated_at)
        """))
        conn.commit()
        print("✅ updated_at 索引创建成功")
    except Exception as e:
        print(f"⚠️  索引创建警告：{e}")

print("\n🎉 数据库结构更新完成！")
