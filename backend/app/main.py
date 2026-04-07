import sys
import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, history, rewrite, config, admin_manage, admin, defense
from app.core.config import settings
from app.db.session import get_engine

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='=== %(message)s ===',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

logger.info("Starting AI Rewrite API")
logger.info(f"App name: {settings.app_name}")

# 检查环境变量
database_url = os.environ.get("DATABASE_URL")
if database_url:
    logger.info("DATABASE_URL is configured")
else:
    logger.warning("DATABASE_URL is NOT configured - API will start but DB requests will fail")

# 延迟初始化数据库（不阻塞启动）
logger.info("Database will be initialized on first request (lazy load)")

logger.info("Creating FastAPI app")
app = FastAPI(title=settings.app_name)

logger.info("Adding CORS middleware")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # HF Space 需要
    allow_origin_regex=r"https?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("Registering routers")
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(rewrite.router, prefix="/rewrite", tags=["rewrite"])
app.include_router(defense.router, prefix="/defense", tags=["defense"])
app.include_router(history.router, prefix="/history", tags=["history"])
app.include_router(config.router, prefix="/config", tags=["config"])
app.include_router(admin.router, prefix="/admin/config", tags=["admin-config"])
app.include_router(admin_manage.router, prefix="/admin", tags=["admin-manage"])

@app.get("/health")
def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": "2026.04.07"
    }

@app.get("/db/status")
def db_status():
    """数据库状态检查"""
    try:
        engine = get_engine()
        return {"status": "connected", "database": "postgresql"}
    except Exception as e:
        return {"status": "disconnected", "error": str(e)}

logger.info("AI Rewrite API started successfully")
logger.info(f"Health check: /health")
logger.info(f"DB status check: /db/status")
