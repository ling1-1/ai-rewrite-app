# 📋 阶段 1 实施清单

## ✅ 已完成

- [x] 添加 pgvector 依赖到 requirements.txt
- [x] 更新 RewriteRecord 模型（添加 embedding、metadata 字段）
- [x] 更新数据库会话（添加连接池配置）
- [x] 更新配置文件（添加 Embedding 和 RAG 配置）
- [x] 创建 .env.example 示例文件
- [x] 创建数据库初始化脚本 (init_db.py)
- [x] 创建数据库测试脚本 (test_db.py)

## ⏳ 待完成（需要用户操作）

- [ ] **创建 Neon 账号**
  - 访问 https://neon.tech
  - 注册/登录
  - 创建项目 `ai-rewrite-app`
  - 选择区域 `aws-ap-southeast-1` (新加坡)
  - 获取连接字符串

- [ ] **配置环境变量**
  - 复制 `backend/.env.example` 到 `backend/.env`
  - 填写 DATABASE_URL（Neon 连接字符串）
  - 填写 ANTHROPIC_API_KEY（火山方舟 API Key）
  - 填写 EMBEDDING_API_KEY（与上面相同）

- [ ] **更新 Hugging Face Spaces 环境变量**
  - 访问 Hugging Face Space 设置
  - 添加/更新以下环境变量：
    - DATABASE_URL
    - ANTHROPIC_API_KEY
    - EMBEDDING_API_KEY

- [ ] **运行数据库初始化**
  - `cd backend`
  - `pip install -r requirements.txt`
  - `python scripts/test_db.py` (测试连接)
  - `python scripts/init_db.py` (初始化数据库)

- [ ] **本地测试**
  - `cd backend`
  - `uvicorn app.main:app --reload`
  - 访问 http://localhost:8000/health
  - 测试改写 API

## 📊 验收标准

- [ ] Neon 数据库连接成功
- [ ] pgvector 扩展已安装
- [ ] rewrite_records 表创建成功
- [ ] 向量索引创建成功
- [ ] 本地测试通过

---

**下一步**：阶段 2 - 向量化服务（Embedding API）
