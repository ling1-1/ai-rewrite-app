# 贡献指南

感谢你为 AI 论文改写网站做出贡献！

## 🌿 分支策略

- **main**: 稳定版本，随时可部署
- **dev**: 开发分支，日常开发在此进行
- **feature/***: 功能分支，从 dev 切出，完成后合并回 dev

## 🚀 开发流程

### 1. 开始新功能

```bash
# 切换到 dev 分支并同步最新代码
git checkout dev
git pull origin dev

# 创建功能分支
git checkout -b feature/你的功能名
```

### 2. 开发并提交

```bash
# 开发完成后提交
git add .
git commit -m "feat: 添加用户登录功能"

# 推送到远程
git push -u origin feature/你的功能名
```

### 3. 创建 Pull Request

1. 访问 GitHub 仓库
2. 点击 "Compare & pull request"
3. 填写 PR 描述（参考 PR 模板）
4. 等待审核

### 4. 代码审核

- 至少需要 1 人审核
- 解决所有评论和修改建议
- 审核通过后合并到 dev

## 📝 提交信息规范

使用 [约定式提交](https://www.conventionalcommits.org/) 格式：

- `feat:` 新功能
- `fix:` 修复 bug
- `docs:` 文档更新
- `style:` 代码格式（不影响功能）
- `refactor:` 重构
- `test:` 测试相关
- `chore:` 构建/工具配置

**示例：**
```
feat: 添加用户注册功能
fix: 修复登录时的 CORS 错误
docs: 更新 API 文档
```

## 🐛 报告问题

发现 bug？请创建 Issue 并包含：

1. 问题描述
2. 复现步骤
3. 预期行为
4. 实际行为
5. 环境信息（浏览器、操作系统等）

## 💡 功能建议

有新想法？欢迎创建 Issue 讨论！

## 🔧 本地开发

```bash
# 安装依赖
cd backend && pip install -r requirements.txt
cd ../frontend && npm install

# 启动服务
# 后端：cd backend && uvicorn app.main:app --reload
# 前端：cd frontend && npm run dev
```

## 📞 联系方式

- GitHub Issues: [提问讨论](https://github.com/ling1-1/ai-rewrite-app/issues)
- 项目地址：https://github.com/ling1-1/ai-rewrite-app

---

感谢你的贡献！🎉
