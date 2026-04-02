#!/usr/bin/env python3
"""修复管理员密码"""

from sqlalchemy import create_engine, text
from passlib.context import CryptContext

# 密码加密
ctx = CryptContext(schemes=['pbkdf2_sha256'], deprecated='auto')
password_hash = ctx.hash('admin123456')

# 数据库连接
engine = create_engine(
    "postgresql://neondb_owner:npg_JFMyeh5aIOn8@ep-ancient-moon-a1mkllm1-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"
)

with engine.connect() as conn:
    # 更新管理员密码
    print("🔧 更新管理员密码...")
    conn.execute(text("""
        UPDATE users 
        SET password_hash = :password_hash 
        WHERE username = 'admin'
    """), {"password_hash": password_hash})
    conn.commit()
    
    # 验证
    result = conn.execute(text("SELECT username, password_hash FROM users WHERE username = 'admin'"))
    row = result.first()
    print(f"✅ 管理员密码已更新")
    print(f"  用户名：{row[0]}")
    print(f"  密码哈希：{row[1][:50]}...")

print("\n📝 测试账号信息:")
print("  用户名：admin")
print("  密码：admin123456")
