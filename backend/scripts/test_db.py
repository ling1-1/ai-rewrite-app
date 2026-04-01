#!/usr/bin/env python3
"""
数据库连接测试脚本

测试 Neon 数据库连接是否正常
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy import text
from app.db.session import engine
from app.core.config import settings

def test_connection():
    """测试数据库连接"""
    print("🔍 测试数据库连接...")
    print(f"📊 数据库 URL: {settings.database_url[:50]}...")
    
    try:
        with engine.connect() as conn:
            # 测试基本查询
            result = conn.execute(text("SELECT version()")).fetchone()
            print(f"✅ 连接成功！")
            print(f"📦 PostgreSQL 版本：{result[0][:50]}...")
            
            # 测试 pgvector 扩展
            result = conn.execute(text("SELECT * FROM pg_extension WHERE extname = 'vector'")).fetchone()
            if result:
                print(f"✅ pgvector 扩展已安装")
            else:
                print(f"❌ pgvector 扩展未安装，运行 init_db.py 创建")
            
            # 测试表是否存在
            result = conn.execute(text("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_name = 'rewrite_records'
            """)).fetchone()
            if result:
                print(f"✅ rewrite_records 表已存在")
            else:
                print(f"❌ rewrite_records 表不存在，运行 init_db.py 创建")
        
        print("\n🎉 数据库测试通过！")
        return True
        
    except Exception as e:
        print(f"\n❌ 数据库连接失败：{e}")
        print("\n可能的问题：")
        print("1. DATABASE_URL 未配置或配置错误")
        print("2. 网络连接问题")
        print("3. Neon 项目未创建")
        print("\n解决方法：")
        print("1. 复制 backend/.env.example 到 backend/.env")
        print("2. 填写正确的 DATABASE_URL")
        print("3. 重新运行测试")
        return False

if __name__ == "__main__":
    test_connection()
