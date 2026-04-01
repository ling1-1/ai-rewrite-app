#!/usr/bin/env python3
"""
数据库初始化脚本

功能：
1. 创建 pgvector 扩展（Neon 数据库）
2. 创建数据表
3. 创建向量索引
"""

import sys
from pathlib import Path

# 添加后端路径
ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy import text
from app.db.session import engine
from app.db.base import Base

def init_database():
    """初始化数据库"""
    print("🔧 开始初始化数据库...")
    
    with engine.connect() as conn:
        # 1. 创建 pgvector 扩展（仅 PostgreSQL）
        if "postgresql" in str(engine.url):
            print("📦 创建 pgvector 扩展...")
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            conn.commit()
            print("✅ pgvector 扩展创建成功")
        else:
            print("⚠️  当前使用 SQLite，跳过 pgvector 扩展")
        
        # 2. 创建数据表
        print("📋 创建数据表...")
        try:
            Base.metadata.create_all(bind=engine)
            print("✅ 数据表创建成功")
        except Exception as e:
            print(f"⚠️  数据表创建警告：{e}")
        
        # 3. 创建向量索引（仅 PostgreSQL）
        if "postgresql" in str(engine.url):
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
                print(f"⚠️  向量索引创建失败（可能已存在）: {e}")
        else:
            print("⚠️  SQLite 不支持向量索引")
    
    print("\n🎉 数据库初始化完成！")

if __name__ == "__main__":
    init_database()
