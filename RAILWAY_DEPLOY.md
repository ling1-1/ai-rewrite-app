# Railway 部署指南

**最后更新**: 2026-04-07

---

## 🚀 快速开始

### 步骤 1：登录 Railway

1. 访问：https://railway.app
2. 点击 **"Login"** → 选择 **"GitHub"** 登录
3. 授权 Railway 访问你的 GitHub 账号

---

### 步骤 2：创建项目

1. 点击 **"New Project"**
2. 选择 **"Deploy from GitHub repo"**
3. 选择仓库：`ling1-1/ai-rewrite-app`
4. 选择分支：`dev`
5. 点击 **"Deploy Now"**

---

### 步骤 3：配置环境变量

在 Railway 项目页面，点击 **"Variables"** 标签，添加以下变量：

#### 数据库配置
```
DATABASE_URL=postgresql://neondb_owner:npg_JFMyeh5aIOn8@ep-ancient-moon-a1mkllm1-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require
SECRET_KEY=ai-rewrite-secret-key-2026
```

#### 改写模型配置（火山方舟）
```
ANTHROPIC_API_KEY=你的改写模型 API_KEY
ANTHROPIC_MODEL=doubao-lite-4k-241215
ANTHROPIC_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
ANTHROPIC_MAX_TOKENS=4096
ANTHROPIC_TEMPERATURE=0.7
```

#### Embedding 配置（Voyage AI）
```
EMBEDDING_PROVIDER=voyage
EMBEDDING_API_KEY=pa-aFD5bNMlkUVJSnl590NzowguG0rEG9VdGJyIVOTvgFP
EMBEDDING_MODEL=voyage-4-lite
EMBEDDING_BASE_URL=https://api.voyageai.com/v1
EMBEDDING_DIMENSION=1024
```

#### 向量数据库配置（Qdrant）
```
VECTOR_DB_BACKEND=qdrant
QDRANT_URL=https://9336cc56-3bc3-48d6-807c-e32ba4a9a3ee.us-east-1-1.aws.cloud.qdrant.io:6333
QDRANT_API_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIiwic3ViamVjdCI6ImFwaS1rZXk6YWQ0YWUyMWUtOTIwOS00ZTVjLWFkNGQtOTEwYjJmODY0YmE5In0.MweLuAJhFYP2-V2wjMc7S9lpi06WLx81WbIYbi0Es4g
QDRANT_COLLECTION=ai_rewrite_records_voyage
```

#### 其他配置
```
MAX_UPLOAD_SIZE_MB=10
APP_NAME=JS 论文工作室
ACCESS_TOKEN_EXPIRE_MINUTES=10080
```

---

### 步骤 4：确认端口

1. 点击 **"Settings"** 标签
2. 找到 **"Ports"** 部分
3. 确认 **Primary Port** 是 `7860`

---

### 步骤 5：等待部署

- Railway 会自动构建和部署
- 查看 **"Deployments"** 标签页的实时日志
- 预计时间：3-5 分钟

---

### 步骤 6：测试

部署成功后，访问：
```
https://[你的项目名].up.railway.app/health
```

应该返回：
```json
{"status": "healthy", "app": "JS 论文工作室 API", "version": "2026.04.07"}
```

---

## 💰 费用说明

- **每月 $5** 免费额度
- **计算资源**: $0.0003/分钟
- **网络流量**: $0.10/GB
- **预计**: $0.1-0.3/天

---

## 🔍 故障排查

### 部署失败

查看 **"Deployments"** → 点击最新部署 → 查看日志

### 启动失败

检查日志中的错误信息，确认环境变量已正确配置。

---

## 📞 支持

如有问题，查看 Railway 文档：https://docs.railway.app
