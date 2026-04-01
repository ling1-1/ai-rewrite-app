FROM python:3.12-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制并安装 Python 依赖
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码
COPY backend/ ./backend
COPY api/ ./api

# 设置 PYTHONPATH
ENV PYTHONPATH=/app:/app/backend

# 暴露端口（HF 使用 7860）
EXPOSE 7860

# 启动命令
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "7860"]

# Rebuild trigger: 1775048478
