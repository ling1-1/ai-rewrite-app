---
title: AI Rewrite API
emoji: 📝
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
license: mit
---

# AI Rewrite API - 论文改写服务

基于 RAG（检索增强生成）的学术论文改写服务。

## 🚀 功能特性

- ✅ 向量检索（VikingDB）
- ✅ Few-shot 提示词构建
- ✅ 学术风格改写
- ✅ 支持多种模型（DeepSeek/Claude/Qwen）

## 📋 环境变量配置

在 Settings → Repository secrets 中配置：

| 变量名 | 说明 |
|--------|------|
| `VOLC_AK` | 火山云 Access Key |
| `VOLC_SK` | 火山云 Secret Key |
| `VOLC_REGION` | 地域（cn-beijing） |
| `VIKING_COLLECTION` | VikingDB 数据集名称 |
| `VIKING_INDEX` | VikingDB 索引名称 |
| `ANTHROPIC_API_KEY` | Chat API Key |
| `ANTHROPIC_MODEL` | 模型名称 |
| `ANTHROPIC_BASE_URL` | API 地址 |
| `SECRET_KEY` | JWT 密钥 |
| `DATABASE_URL` | 数据库连接 |

## 🔗 API 文档

**健康检查**:
```bash
curl https://zzz235-ai-rewrite-api.hf.space/health
```

**改写 API**（需要登录 token）:
```bash
curl -X POST https://zzz235-ai-rewrite-api.hf.space/api/rewrite \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"source_text": "机器学习是什么", "use_rag": true}'
```

## 📊 技术栈

- **后端**: FastAPI + SQLAlchemy
- **向量数据库**: VikingDB
- **Chat 模型**: DeepSeek-V3.2 / Claude
- **部署**: Hugging Face Spaces (Docker)

## 🎯 模型切换

只需修改环境变量即可切换模型：

```bash
# DeepSeek
ANTHROPIC_MODEL=ep-20260116111114-pkwld
ANTHROPIC_BASE_URL=https://ark.cn-beijing.volces.com/api/v3

# Claude
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
ANTHROPIC_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
```

## 📝 License

MIT License
