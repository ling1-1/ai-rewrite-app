#!/usr/bin/env python3
"""数据库迁移：添加历史记录新字段"""

import os
from sqlalchemy import create_engine, text

db_url = os.getenv('DATABASE_URL')
print(f"🔧 连接数据库...")

engine = create_engine(db_url)

with engine.connect() as conn:
    print("\n📝 添加字段到 rewrite_records 表...")
    
    # 添加 name 字段
    try:
        conn.execute(text("ALTER TABLE rewrite_records ADD COLUMN IF NOT EXISTS name TEXT"))
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
    
    conn.commit()

print("\n" + "="*60)
print("✅ 数据库迁移完成！")
print("="*60)
