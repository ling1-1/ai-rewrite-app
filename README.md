# AI 文本改写网站 MVP

当前仓库已经按第一版需求搭好基础骨架：

- `frontend/`：Vue 3 + Vite 前端
- `backend/`：FastAPI + SQLAlchemy 后端
- `docker-compose.yml`：本地 MySQL

## 当前功能范围

- 用户注册 / 登录
- 左侧输入原文
- 右侧展示处理结果
- 历史记录列表
- 演示版改写逻辑
- Claude API 改写服务接入位

## 当前数据库说明

- 当前默认数据库已经切换为 `MySQL`
- 后端通过 `SQLAlchemy + PyMySQL` 连接 MySQL
- 首次启动后端时会自动创建 `users` 和 `rewrite_records` 表

## 本地开发

### 1. 启动数据库

```bash
docker compose up -d
```

如果你已经在 Mac 本机安装好了 MySQL，也可以不用 Docker，先创建数据库：

```sql
CREATE DATABASE rewrite_app CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2. 启动后端

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

注意把 `.env` 里的 `DATABASE_URL` 改成你自己的 MySQL 密码，例如：

```env
DATABASE_URL=mysql+pymysql://root:你的MySQL密码@127.0.0.1:3306/rewrite_app
```

同时配置 Claude API：

```env
ANTHROPIC_API_KEY=你的AnthropicKey
ANTHROPIC_MODEL=claude-sonnet-4-20250514
ANTHROPIC_BASE_URL=https://api.anthropic.com
ANTHROPIC_MAX_TOKENS=4096
ANTHROPIC_TEMPERATURE=0.4
```

### 3. 启动前端

```bash
cd frontend
npm install
npm run dev
```

## 默认地址

- 前端：`http://localhost:5173`
- 后端：`http://127.0.0.1:8000`
- API 文档：`http://127.0.0.1:8000/docs`

## GitHub + Vercel 发布

仓库已经调整为可直接从根目录部署到 Vercel：

- 根目录 `index.py` 暴露 FastAPI 应用
- 根目录 `requirements.txt` 提供 Python 依赖
- 根目录 `package.json` 会构建 `frontend/` 到 `public/`
- `vercel.json` 已配置 SPA 路由回退

### Vercel 需要配置的环境变量

至少配置以下变量：

```env
DATABASE_URL=mysql+pymysql://用户名:密码@你的公网MySQL地址:3306/rewrite_app
SECRET_KEY=一段足够长的随机字符串
ANTHROPIC_API_KEY=你的AnthropicKey
ANTHROPIC_MODEL=claude-sonnet-4-20250514
ANTHROPIC_BASE_URL=https://api.anthropic.com
ANTHROPIC_MAX_TOKENS=4096
ANTHROPIC_TEMPERATURE=0.4
```

注意：

- Vercel 不能直接使用你本机的 `127.0.0.1:3306`
- 生产环境必须换成公网可访问的 MySQL
- 前端生产环境默认请求同域 `/api`
