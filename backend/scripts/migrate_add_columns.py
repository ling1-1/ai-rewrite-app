#!/usr/bin/env python3
"""添加 metadata 和 similarity_score 列"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from sqlalchemy import text
from app.db.session import engine

print("🔧 开始更新数据库结构...")

with engine.connect() as conn:
    # 检查 metadata 列
    result = conn.execute(text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'rewrite_records' AND column_name = 'metadata'
    """))
    
    if result.fetchone():
        print("✅ metadata 列已存在，跳过")
    else:
        print("📦 添加 metadata 列...")
        conn.execute(text("""
            ALTER TABLE rewrite_records 
            ADD COLUMN metadata JSONB DEFAULT '{}'
        """))
        conn.commit()
        print("✅ metadata 列添加成功")
    
    # 检查 similarity_score 列
    result = conn.execute(text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'rewrite_records' AND column_name = 'similarity_score'
    """))
    
    if result.fetchone():
        print("✅ similarity_score 列已存在，跳过")
    else:
        print("📦 添加 similarity_score 列...")
        conn.execute(text("""
            ALTER TABLE rewrite_records 
            ADD COLUMN similarity_score FLOAT
        """))
        conn.commit()
        print("✅ similarity_score 列添加成功")

print("\n🎉 数据库结构更新完成！")
