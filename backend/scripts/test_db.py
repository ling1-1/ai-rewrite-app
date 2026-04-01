#!/usr/bin/env python3
"""测试数据库连接和表结构"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from sqlalchemy import text
from app.db.session import engine

print("🔍 测试数据库连接...")

with engine.connect() as conn:
    # 检查表
    result = conn.execute(text("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """))
    tables = [r[0] for r in result.fetchall()]
    print(f"📊 表列表：{tables}")
    
    # 检查 pgvector 扩展
    result = conn.execute(text("""
        SELECT extname FROM pg_extension WHERE extname = 'vector'
    """))
    ext = result.fetchone()
    if ext:
        print("✅ pgvector 扩展已安装")
    else:
        print("❌ pgvector 扩展未安装")
    
    # 检查 rewrite_records 表
    if 'rewrite_records' in tables:
        print("✅ rewrite_records 表已存在")
        
        # 检查 embedding 列
        result = conn.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'rewrite_records' AND column_name = 'embedding'
        """))
        col = result.fetchone()
        if col:
            print(f"✅ embedding 列已存在：{col}")
        else:
            print("❌ embedding 列不存在")
    else:
        print("❌ rewrite_records 表不存在")

print("\n✅ 测试完成！")
