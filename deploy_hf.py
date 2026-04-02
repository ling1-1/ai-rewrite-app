#!/usr/bin/env python3
"""推送项目到 Hugging Face Spaces"""
from huggingface_hub import HfApi, login
import os

# 配置
SPACE_ID = "zzz235/ai-rewrite-api"
REPO_TYPE = "space"
FOLDER = "/Users/baijingting/.openclaw/workspace/ai-rewrite-app"

# 获取 HF token
token = os.environ.get("HF_TOKEN")
if not token:
    print("❌ 未设置 HF_TOKEN 环境变量")
    exit(1)

# 登录
login(token=token)
api = HfApi()

print(f"📤 开始推送到 {SPACE_ID}...")

try:
    # 上传文件夹
    api.upload_folder(
        folder_path=FOLDER,
        repo_id=SPACE_ID,
        repo_type=REPO_TYPE,
        commit_message="更新项目代码",
        ignore_patterns=["__pycache__", "*.pyc", ".git", "venv", "node_modules", ".env", "*.log", "deploy_hf.py"],
    )
    print(f"✅ 推送成功！")
    print(f"🔗 查看：https://huggingface.co/spaces/{SPACE_ID}")
except Exception as e:
    print(f"❌ 推送失败：{e}")
    exit(1)
