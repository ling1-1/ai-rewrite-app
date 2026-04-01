# 🚀 迁移到 Neon 数据库指南

## 步骤 1: 创建 Neon 账号

1. 访问 https://neon.tech
2. 点击 "Sign Up"
3. 使用 GitHub/Google 账号登录（推荐）或邮箱注册

## 步骤 2: 创建项目

1. 登录后点击 "Create a project"
2. 填写项目信息：
   - **Project name**: `ai-rewrite-app`
   - **Database name**: `rewrite_app`
   - **Region**: 选择最近的（推荐 `aws-ap-southeast-1` 新加坡）
3. 点击 "Create"

## 步骤 3: 获取连接字符串

1. 在项目 Dashboard 页面，找到 "Connection Details"
2. 复制 **Connection string** (Pooler 模式)
   - 格式：`postgresql://user:password@host.region.aws.neon.tech/dbname?sslmode=require`
3. ⚠️ 重要：保存好密码，后面要用

## 步骤 4: 更新 Hugging Face 环境变量

在 Hugging Face Space Settings → Repository secrets：

1. 删除旧的 `DATABASE_URL` (SQLite)
2. 添加新的 `DATABASE_URL`：
   ```
   postgresql://user:password@host.region.aws.neon.tech/rewrite_app?sslmode=require
   ```

## 步骤 5: 创建数据库表

Neon 会自动创建数据库，但需要手动创建表。

### 方式 A: 使用 Neon SQL Editor（推荐）

1. 在 Neon Dashboard 点击 "SQL Editor"
2. 运行以下 SQL：

```sql
-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 改写记录表
CREATE TABLE IF NOT EXISTS rewrite_records (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    original_text TEXT NOT NULL,
    rewritten_text TEXT NOT NULL,
    model_used VARCHAR(100),
    settings JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_rewrite_records_user_id ON rewrite_records(user_id);
CREATE INDEX IF NOT EXISTS idx_rewrite_records_created_at ON rewrite_records(created_at);
```

### 方式 B: 使用应用程序自动创建

如果你的 FastAPI 应用配置了 `SQLAlchemy` 自动迁移：

```python
# backend/app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 自动创建表
from backend.app.models.base import Base
Base.metadata.create_all(bind=engine)
```

应用启动时会自动创建表。

## 步骤 6: 测试连接

### 本地测试

```bash
# 安装 Neon 依赖
pip install psycopg2-binary

# 测试连接
python3 << 'PYTHON'
import os
from sqlalchemy import create_engine, text

# 替换为你的 Neon 连接字符串
DATABASE_URL = "postgresql://user:password@host.region.aws.neon.tech/rewrite_app?sslmode=require"

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        print(f"✅ 连接成功！")
        print(f"PostgreSQL 版本：{result.fetchone()[0]}")
except Exception as e:
    print(f"❌ 连接失败：{e}")
PYTHON
```

### 远程测试（Hugging Face）

1. 在 Hugging Face Space 点击 "Logs" 标签页
2. 查看应用启动日志
3. 寻找类似信息：
   ```
   INFO:     Application startup complete.
   ```
4. 如果有数据库错误，会显示连接失败信息

## 步骤 7: 数据迁移（可选）

如果你之前在 SQLite 有数据需要迁移：

### 导出 SQLite 数据

```bash
cd ~/.openclaw/workspace/breeze1012-project

# 使用 sqlite3 导出
sqlite3 backend/rewrite_app.db << 'SQL'
.mode csv
.headers on
.output users.csv
SELECT * FROM users;
.output rewrite_records.csv
SELECT * FROM rewrite_records;
SQL
```

### 导入到 Neon

```bash
# 使用 psql 导入
psql "postgresql://user:password@host.region.aws.neon.tech/rewrite_app?sslmode=require" << 'SQL'
\copy users FROM 'users.csv' WITH (FORMAT csv, HEADER true);
\copy rewrite_records FROM 'rewrite_records.csv' WITH (FORMAT csv, HEADER true);
SQL
```

## ⚠️ 注意事项

1. **连接池** - Neon 推荐使用 Pooler 模式（默认端口 6543）
2. **SSL 必需** - 连接字符串必须包含 `?sslmode=require`
3. **超时设置** - 建议设置连接超时（30 秒）
4. **自动重连** - SQLAlchemy 默认会重连

## 🎉 完成！

现在你的数据库已经迁移到 Neon，重启后数据不会丢失！

---

**下一步**：
- [ ] 创建 Neon 账号和项目
- [ ] 更新 Hugging Face 环境变量
- [ ] 创建数据库表
- [ ] 测试连接
- [ ] 验证功能正常
