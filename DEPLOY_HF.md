# AI 论文改写后端 - Hugging Face Spaces 部署指南

## 📋 部署步骤

### 1. 创建 Hugging Face 账号
访问 https://huggingface.co 并注册/登录

### 2. 创建新的 Space
1. 访问 https://huggingface.co/spaces
2. 点击 "Create new Space"
3. 填写信息：
   - **Space name**: `ai-rewrite-api`（或你喜欢的名字）
   - **License**: MIT
   - **Space SDK**: 选择 **Docker**
   - **Visibility**: Public 或 Private

### 3. 部署方式（二选一）

#### 方式 A：通过 GitHub 部署（推荐）
1. 在 Space 页面点击 "Files" → "Add file" → "Import from GitHub"
2. 输入你的 GitHub 仓库地址：`ling1-1/ai-rewrite-app`
3. 选择要导入的文件：
   - `Dockerfile`
   - `.dockerignore`
   - `backend/` 目录
   - `api/` 目录
   - `backend/requirements.txt`

#### 方式 B：直接上传文件
1. 在 Space 页面点击 "Files"
2. 上传以下文件：
   - `Dockerfile`
   - `.dockerignore`
   - `backend/` 目录（所有文件）
   - `api/` 目录（所有文件）
   - `backend/requirements.txt`

### 4. 配置环境变量

在 Space 页面点击 "Settings" → "Repository secrets"，添加以下环境变量：

| 变量名 | 值 | 说明 |
|--------|-----|------|
| `SECRET_KEY` | `your-secret-key-here` | JWT 密钥（可以用任意随机字符串） |
| `DATABASE_URL` | `sqlite:///./rewrite_app.db` | 数据库连接（SQLite） |
| `ANTHROPIC_API_KEY` | `你的火山方舟 API Key` | 火山方舟 API Key |
| `ANTHROPIC_MODEL` | `doubao-lite-4k-241215` | 豆包模型 |
| `ANTHROPIC_BASE_URL` | `https://ark.cn-beijing.volces.com/api/v3` | 火山方舟 API 地址 |
| `ANTHROPIC_MAX_TOKENS` | `4096` | 最大 token 数 |
| `ANTHROPIC_TEMPERATURE` | `0.7` | 温度参数 |

### 5. 等待部署完成

Space 会自动构建 Docker 镜像并启动服务，大约需要 2-5 分钟。

### 6. 获取 API 地址

部署完成后，你的 API 地址是：
```
https://huggingface.co/spaces/你的用户名/ai-rewrite-api
```

API 端点示例：
- Health Check: `https://你的用户名-ai-rewrite-api.hf.space/api/health`
- 注册：`https://你的用户名-ai-rewrite-api.hf.space/api/auth/register`
- 登录：`https://你的用户名-ai-rewrite-api.hf.space/api/auth/login`

---

## 🧪 本地测试 Docker

在推送到 Hugging Face 之前，可以先在本地测试：

```bash
# 进入项目目录
cd ~/.openclaw/workspace/breeze1012-project

# 构建 Docker 镜像
docker build -t ai-rewrite-api .

# 运行容器
docker run -p 7860:7860 \
  -e SECRET_KEY="test-secret-key" \
  -e DATABASE_URL="sqlite:///./rewrite_app.db" \
  -e ANTHROPIC_API_KEY="你的 API Key" \
  -e ANTHROPIC_MODEL="doubao-lite-4k-241215" \
  -e ANTHROPIC_BASE_URL="https://ark.cn-beijing.volces.com/api/v3" \
  ai-rewrite-api

# 测试 API
curl http://localhost:7860/api/health
```

---

## 🔧 更新前端配置

后端部署完成后，需要更新 Vercel 前端的 API 地址。

由于前端已经部署到 Vercel，最简单的方法是：

1. 在 Vercel 项目设置中添加环境变量 `VITE_API_BASE_URL`
2. 或者修改前端代码中的 API 基础 URL

---

## ⚠️ 注意事项

1. **Hugging Face Spaces 是公开的** - 如果选择 Public，任何人都可以访问你的 API
2. **免费资源限制** - CPU 2 核，RAM 16GB
3. **不会休眠** - 与 Render 不同，Hugging Face Spaces 不会休眠
4. **数据库持久化** - 使用 SQLite 时，数据会保存在容器中，重启会丢失。建议使用外部数据库或 Hugging Face 的持久化存储

---

## 📞 需要帮助？

如果在部署过程中遇到问题，可以：
1. 查看 Space 的 "Logs" 标签页查看构建日志
2. 检查环境变量是否正确配置
3. 确保 Dockerfile 中的路径正确
