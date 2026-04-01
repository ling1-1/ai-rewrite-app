# 🚀 Hugging Face Spaces 部署指南

## 📋 部署步骤

### 1. 创建 Space

1. 访问 https://huggingface.co/spaces
2. 点击 **"Create new Space"**
3. 配置：
   - **Space name**: `ai-rewrite-api`（或你喜欢的名字）
   - **License**: MIT
   - **Space SDK**: 选择 **Docker** ⚠️ 重要
   - **Visibility**: Public 或 Private

### 2. 关联 GitHub 仓库

**方式 A: 直接导入 GitHub**（推荐）

1. 在 Space 页面点击 **"Files"** → **"Add file"** → **"Import from GitHub"**
2. 输入仓库地址：`ling1-1/ai-rewrite-app`
3. 选择分支：`feature/rag-development`
4. 点击 **"Import"**

**方式 B: 手动推送**

```bash
# 克隆 HF Space 仓库
git clone https://huggingface.co/spaces/你的用户名/ai-rewrite-api hf-space
cd hf-space

# 复制项目文件
cp -r ../breeze1012-project/* .

# 推送到 HF
git add .
git commit -m "Initial commit"
git push
```

### 3. 配置环境变量

在 Space 页面：

1. 点击 **"Settings"** 标签
2. 滚动到 **"Repository secrets"** 部分
3. 点击 **"New secret"**
4. 添加以下环境变量：

| 变量名 | 值 | 说明 |
|--------|-----|------|
| `VOLC_AK` | 你的 AccessKeyID | 火山云 AK |
| `VOLC_SK` | 你的 SecretAccessKey | 火山云 SK |
| `VOLC_REGION` | `cn-beijing` | 地域 |
| `VIKING_COLLECTION` | `ai_rewrite_kb` | 数据集名称 |
| `VIKING_INDEX` | `ai_rewrite_kb_index` | 索引名称 |
| `ANTHROPIC_API_KEY` | 你的火山方舟 APIKey | Chat API 密钥 |
| `ANTHROPIC_MODEL` | `ep-20260116111114-pkwld` | DeepSeek-V3.2 接入点 |
| `ANTHROPIC_BASE_URL` | `https://ark.cn-beijing.volces.com/api/v3` | API 地址 |
| `SECRET_KEY` | 随机字符串 | JWT 密钥 |
| `DATABASE_URL` | `sqlite:///./rewrite_app.db` | SQLite 数据库 |

### 4. 等待部署

- Space 会自动构建 Docker 镜像（约 2-5 分钟）
- 在 **"Logs"** 标签页查看构建进度
- 状态变为 **"Running"** 表示部署成功

### 5. 测试 API

部署完成后，你的 API 地址是：
```
https://你的用户名-ai-rewrite-api.hf.space
```

**测试健康检查**：
```bash
curl https://你的用户名-ai-rewrite-api.hf.space/health
```

**测试改写 API**（需要登录 token）：
```bash
curl -X POST https://你的用户名-ai-rewrite-api.hf.space/api/rewrite \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"source_text": "机器学习是什么", "use_rag": true}'
```

---

## 🔧 故障排查

### 问题 1: 构建失败

**错误**: `No module named 'vikingdb'`

**解决**: 确保 `requirements.txt` 包含 `vikingdb-python-sdk==0.1.18`

### 问题 2: 环境变量未生效

**检查**:
1. 确认环境变量名称正确（大小写敏感）
2. 确认在 Settings → Repository secrets 中配置
3. 重启 Space（点击 Settings → Factory reboot）

### 问题 3: VikingDB 检索失败

**检查**:
1. 确认 VOLC_AK 和 VOLC_SK 正确
2. 确认数据集和索引已创建
3. 查看日志中的具体错误信息

---

## 📊 成本说明

### Hugging Face Spaces

- **CPU Basic**: 免费（2 vCPU, 16GB RAM）
- **Persistent Storage**: $5/月（20GB，可选）

### 火山云 VikingDB

- **存储**: ¥0.0015/GB/小时
- **计算**: ¥0.45/CU/小时
- **Embedding**: ¥0.0005/千 tokens

### 火山方舟 Chat API

- **DeepSeek-V3.2**: 约¥0.01/次（按 token 计费）

**预计月成本**: ¥100-300（根据使用量）

---

## 🎯 下一步

部署成功后：

1. **测试完整流程** - 从前端调用 API
2. **同步历史数据** - 调用 `/sync-to-viking` 接口
3. **监控使用情况** - 查看 HF 和火山云的使用量

---

**祝你部署成功！** 🚀
