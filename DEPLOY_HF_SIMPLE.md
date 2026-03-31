# 🚀 Hugging Face Spaces 快速部署指南

## ✅ 已完成的准备工作

1. ✅ Dockerfile 已创建
2. ✅ .dockerignore 已创建
3. ✅ Docker 镜像本地构建成功 (644MB)

---

## 📋 部署步骤（5 分钟完成）

### 步骤 1: 创建 Hugging Face 账号
1. 访问 https://huggingface.co
2. 注册/登录账号

### 步骤 2: 创建 Space
1. 访问 https://huggingface.co/new-space
2. 填写：
   - **Space name**: `ai-rewrite-api`
   - **License**: MIT
   - **Space SDK**: 选择 **Docker** ⚠️ 重要！
   - **Visibility**: Public 或 Private

### 步骤 3: 上传代码

**方式 A: 通过 Git 推送（推荐）**

```bash
# 1. 克隆 Space 仓库
cd ~/.openclaw/workspace/breeze1012-project
git clone https://huggingface.co/spaces/你的用户名/ai-rewrite-api hf-deploy

# 2. 复制必要文件
cp Dockerfile hf-deploy/
cp .dockerignore hf-deploy/
cp -r backend hf-deploy/
cp -r api hf-deploy/

# 3. 推送到 Hugging Face
cd hf-deploy
git add .
git commit -m "Initial commit: AI Rewrite API"
git push
```

**方式 B: 网页上传**
1. 在 Space 页面点击 "Files"
2. 点击 "Add file" → "Upload file"
3. 上传：
   - `Dockerfile`
   - `.dockerignore`
   - `backend/` 目录
   - `api/` 目录

### 步骤 4: 配置环境变量

在 Space 页面：
1. 点击 "Settings" 标签
2. 滚动到 "Repository secrets" 部分
3. 点击 "New secret"
4. 添加以下环境变量：

| Name | Value |
|------|-------|
| `SECRET_KEY` | `ai-rewrite-secret-key-2026` |
| `DATABASE_URL` | `sqlite:///./rewrite_app.db` |
| `ANTHROPIC_API_KEY` | `d78c3528-7a65-4746-a704-43660d80493d` |
| `ANTHROPIC_MODEL` | `doubao-lite-4k-241215` |
| `ANTHROPIC_BASE_URL` | `https://ark.cn-beijing.volces.com/api/v3` |
| `ANTHROPIC_MAX_TOKENS` | `4096` |
| `ANTHROPIC_TEMPERATURE` | `0.7` |

### 步骤 5: 等待部署

- Space 会自动构建 Docker 镜像（约 2-5 分钟）
- 在 "Logs" 标签页可以查看构建进度
- 看到 "Running" 状态表示部署成功

---

## 🧪 测试 API

部署完成后，你的 API 地址是：

```
https://你的用户名-ai-rewrite-api.hf.space
```

**测试命令：**

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

## 🔧 更新 Vercel 前端

后端部署成功后，需要更新前端配置：

1. 访问 https://vercel.com
2. 进入 `ai-rewrite-app-frontend` 项目
3. 点击 "Settings" → "Environment Variables"
4. 添加 `VITE_API_BASE_URL` = `https://你的用户名-ai-rewrite-api.hf.space`
5. 重新部署前端

---

## ⚠️ 注意事项

1. **Hugging Face Spaces 是公开的** - 如果选择 Public，任何人都可以访问
2. **免费资源** - CPU 2 核，RAM 16GB
3. **不会休眠** - 与 Render 不同，Hugging Face Spaces 不会休眠
4. **数据库持久化** - SQLite 数据会保存在容器中，建议使用外部数据库

---

## 📞 遇到问题？

1. **构建失败**: 查看 "Logs" 标签页查看详细错误
2. **环境变量问题**: 确保在 Settings 中正确配置
3. **端口问题**: Dockerfile 中使用 7860 端口（Hugging Face 默认）

---

**现在就开始部署吧！** 🚀
