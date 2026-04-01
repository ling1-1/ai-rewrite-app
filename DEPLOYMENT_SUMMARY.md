# 🚀 AI 论文改写网站 - 部署经验总结

**项目**: AI 文本改写网站 (Breeze1012)  
**GitHub**: https://github.com/ling1-1/ai-rewrite-app  
**部署时间**: 2026-03-31 ~ 2026-04-01  
**部署架构**: 前后端分离

---

## 📊 最终部署架构

```
┌─────────────────────────────────────────────────────────┐
│                      用户访问                            │
└───────────────────┬─────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
        ▼                       ▼
┌───────────────┐       ┌──────────────────┐
│   Vercel      │       │ Hugging Face     │
│   (前端)      │──────▶│ Spaces (后端)    │
│               │  API  │                  │
│ 静态资源      │ 调用  │ FastAPI 服务     │
└───────────────┘       └──────────────────┘
```

---

## 🎯 部署历程

### 第一阶段：Vercel 前后端一体部署（❌ 失败）

**时间**: 2026-03-31 14:38-16:25

**尝试方案**:
- 使用 Vercel 同时部署前端和后端
- 配置 `vercel.json` 路由规则
- 使用 `@vercel/python` 构建器

**遇到的问题**:
1. **构建命令路径错误** - Vercel 找不到正确的构建脚本
2. **前后端一起部署复杂** - Python 和 Node.js 构建冲突
3. **npm 构建失败** - 依赖安装超时

**结果**: 前端部署成功（旧版本），后端构建失败

**教训**:
- ⚠️ Vercel 不适合复杂的全栈应用（前后端技术栈不同）
- ⚠️ Python + Node.js 混合项目需要分开部署
- ⚠️ 构建超时问题：Vercel 免费额度有限

---

### 第二阶段：前后端分离部署（✅ 成功）

**时间**: 2026-04-01

**新架构**:
- **前端**: Vercel（静态资源 + Vue 3）
- **后端**: Hugging Face Spaces（Docker 容器）

**成功关键**:
1. **前后端彻底分离** - 不再尝试在 Vercel 部署 Python
2. **使用 Docker** - Hugging Face Spaces 支持 Docker 部署
3. **环境变量隔离** - 前后端各自管理配置

---

## 📦 后端部署（Hugging Face Spaces）

### 部署步骤

#### 1. 创建 Space
- 访问 https://huggingface.co/new-space
- Space name: `ai-rewrite-api`
- SDK: **Docker** ⚠️ 重要
- Visibility: Public/Private

#### 2. 准备文件

**必需文件**:
```
breeze1012-project/
├── Dockerfile              # ✅ 已创建
├── .dockerignore           # ✅ 已创建
├── backend/
│   ├── requirements.txt    # ✅ Python 依赖
│   └── app/
│       ├── main.py         # ✅ FastAPI 入口
│       ├── api/            # ✅ API 路由
│       ├── models/         # ✅ 数据模型
│       ├── schemas/        # ✅ 数据验证
│       ├── services/       # ✅ 业务逻辑
│       └── core/           # ✅ 核心配置
│       └── db/             # ✅ 数据库配置
```

#### 3. 配置环境变量

在 Space Settings → Repository secrets 添加：

| 变量名 | 值 | 说明 |
|--------|-----|------|
| `SECRET_KEY` | `ai-rewrite-secret-key-2026` | JWT 密钥 |
| `DATABASE_URL` | `sqlite:///./rewrite_app.db` | SQLite 数据库 |
| `ANTHROPIC_API_KEY` | `d78c3528-7a65-4746-a704-43660d80493d` | 火山方舟 API Key |
| `ANTHROPIC_MODEL` | `doubao-lite-4k-241215` | 豆包模型 |
| `ANTHROPIC_BASE_URL` | `https://ark.cn-beijing.volces.com/api/v3` | 火山方舟 API 地址 |
| `ANTHROPIC_MAX_TOKENS` | `4096` | 最大 token 数 |
| `ANTHROPIC_TEMPERATURE` | `0.7` | 温度参数 |

#### 4. 部署方式

**方式 A: Git 推送（推荐）**
```bash
cd ~/.openclaw/workspace/breeze1012-project
git clone https://huggingface.co/spaces/你的用户名/ai-rewrite-api hf-deploy
cp Dockerfile .dockerignore hf-deploy/
cp -r backend api hf-deploy/
cd hf-deploy && git add . && git commit -m "Deploy" && git push
```

**方式 B: 网页上传**
- 在 Space 页面点击 "Files" → "Add file" → "Upload file"
- 上传 Dockerfile, .dockerignore, backend/, api/

#### 5. 等待部署
- 构建时间：2-5 分钟
- 查看 Logs 标签页监控进度
- 状态变为 "Running" 表示成功

### API 地址

```
https://你的用户名-ai-rewrite-api.hf.space
```

**测试端点**:
```bash
# Health Check
curl https://你的用户名-ai-rewrite-api.hf.space/api/health

# 注册
curl -X POST https://你的用户名-ai-rewrite-api.hf.space/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@test.com","password":"test123"}'

# 登录
curl -X POST https://你的用户名-ai-rewrite-api.hf.space/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test123"}'
```

---

## 🌐 前端部署（Vercel）

### 部署步骤

#### 1. 连接 GitHub 仓库
- 访问 https://vercel.com
- Import Project → 选择 `ling1-1/ai-rewrite-app`

#### 2. 配置构建设置

**Framework Preset**: Vite  
**Root Directory**: `frontend`  
**Build Command**: `npm run build`  
**Output Directory**: `dist`

#### 3. 配置环境变量

在 Vercel Settings → Environment Variables 添加：

| 变量名 | 值 | 说明 |
|--------|-----|------|
| `VITE_API_BASE_URL` | `https://你的用户名-ai-rewrite-api.hf.space` | 后端 API 地址 |

#### 4. 部署
- 点击 Deploy
- 等待构建完成（约 1-2 分钟）
- 获取生产环境 URL

### 前端地址

```
https://ai-rewrite-app-frontend.vercel.app
```

---

## ⚠️ 踩过的坑

### 1. Vercel 前后端混合部署失败

**问题**: 尝试在 Vercel 同时部署 Vue 前端和 FastAPI 后端

**原因**:
- Vercel 对 Python 支持有限（主要是 Serverless Functions）
- 前端构建（npm）和后端构建（pip）冲突
- 免费额度限制导致构建超时

**解决**: 前后端分离，后端迁移到 Hugging Face

---

### 2. Hugging Face Docker 构建失败

**问题**: Dockerfile 路径错误

**原因**: WORKDIR 和 COPY 路径不匹配

**解决**: 
```dockerfile
# ✅ 正确配置
FROM python:3.12-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
COPY backend/ ./backend
COPY api/ ./api
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port": "7860"]
```

---

### 3. 前端无法调用后端 API

**问题**: CORS 错误或 404

**原因**:
- 前端 API 地址配置错误
- 后端未配置 CORS

**解决**:
1. 在 Vercel 配置 `VITE_API_BASE_URL`
2. 后端 FastAPI 添加 CORS 中间件：
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该指定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### 4. 数据库持久化问题

**问题**: Hugging Face Spaces 重启后数据丢失

**原因**: 容器重启后 SQLite 文件被清除

**解决**:
- **短期**: 使用 SQLite（测试环境）
- **长期**: 迁移到外部数据库（如 Supabase、Neon、Railway）

---

## 📊 平台对比

| 特性 | Vercel | Hugging Face Spaces |
|------|--------|---------------------|
| **前端支持** | ✅ 优秀（静态/Vue/React） | ❌ 不适合 |
| **后端支持** | ⚠️ 有限（Serverless） | ✅ 优秀（Docker） |
| **Python 支持** | ⚠️ Serverless Functions | ✅ 完整（容器） |
| **构建超时** | 60 秒（免费） | 15 分钟 |
| **资源限制** | 100GB 带宽/月 | CPU 2 核，RAM 16GB |
| **休眠** | 无（Serverless 按需） | 无（持续运行） |
| **数据库** | 需外部 | 可内部（但重启丢失） |
| **适合场景** | 前端、静态站点 | AI 应用、后端 API |

---

## ✅ 当前状态（2026-04-01）

### 已完成
- [x] 前后端分离架构设计
- [x] Hugging Face Spaces 后端部署
- [x] Vercel 前端部署
- [x] 环境变量配置
- [x] CORS 配置
- [x] Dockerfile 创建

### 待完成
- [ ] 数据库迁移到外部（避免重启丢失）
- [ ] 域名绑定（可选）
- [ ] HTTPS 证书（Hugging Face 已提供）
- [ ] 监控和日志（Hugging Face 提供基础日志）
- [ ] 性能优化

---

## 🔧 后续优化建议

### 1. 数据库升级

**当前**: SQLite（容器内，重启丢失）  
**建议**: 
- **Supabase** (PostgreSQL，免费额度够用)
- **Neon** (Serverless PostgreSQL，免费)
- **Railway** (PostgreSQL，$5/月)

**迁移步骤**:
```bash
# 1. 创建 Supabase 数据库
# 2. 获取连接字符串
# 3. 更新 Hugging Face 环境变量
DATABASE_URL=postgresql://user:pass@host:5432/rewrite_app
```

---

### 2. 监控和告警

**建议添加**:
- **Sentry** - 错误追踪
- **UptimeRobot** - 服务可用性监控
- **Hugging Face Logs** - 查看应用日志

---

### 3. 性能优化

**前端**:
- 启用 Gzip 压缩（Vercel 自动）
- 图片懒加载
- 代码分割

**后端**:
- 添加 Redis 缓存（改写结果）
- 数据库连接池
- API 限流

---

## 📞 快速参考

### 项目目录
```
~/.openclaw/workspace/breeze1012-project/
├── frontend/           # Vue 3 前端
├── backend/            # FastAPI 后端
├── api/                # Vercel API 适配层
├── Dockerfile          # Hugging Face 部署配置
├── vercel.json         # Vercel 配置
└── DEPLOYMENT_SUMMARY.md  # 本文档
```

### 部署命令

**后端（Hugging Face）**:
```bash
cd ~/.openclaw/workspace/breeze1012-project
git clone https://huggingface.co/spaces/USERNAME/ai-rewrite-api hf-deploy
cp Dockerfile .dockerignore backend/ api/ hf-deploy/
cd hf-deploy && git push
```

**前端（Vercel）**:
```bash
# 通过 Vercel CLI
cd frontend
vercel --prod
```

---

## 🎓 学到的经验

1. **前后端分离是王道** - 不要试图在一个平台部署所有东西
2. **选择合适的平台** - Vercel 适合前端，Hugging Face 适合 AI 后端
3. **Docker 是救星** - 容器化部署避免了环境兼容问题
4. **环境变量管理** - 敏感信息不要提交到 Git
5. **数据库持久化** - 容器重启会丢失数据，要用外部数据库
6. **CORS 配置** - 前后端分离必须处理跨域
7. **构建超时** - 免费额度有限，复杂构建要考虑付费方案

---

**最后更新**: 2026-04-01  
**作者**: 艾克斯  
**状态**: ✅ 部署成功，待优化
