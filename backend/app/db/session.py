from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# 不立即创建连接池，延迟到第一次使用时
_engine = None
SessionLocal = None

def get_engine():
    """延迟创建数据库引擎"""
    global _engine, SessionLocal
    
    if _engine is None:
        logger.info("=== Creating database engine (lazy load) ===")
        
        engine_kwargs = {
            "future": True,
            "echo": False,  # 生产环境关闭 SQL 日志
        }
        
        # PostgreSQL 连接池配置（Neon / HF）
        if settings.database_url.startswith("postgresql"):
            engine_kwargs.update({
                "poolclass": QueuePool,
                "pool_size": 5,  # 减小池大小
                "max_overflow": 10,
                "pool_pre_ping": True,
                "pool_recycle": 1800,
                "connect_args": {
                    "connect_timeout": 30,  # 增加超时时间
                    "sslmode": "require",
                },
            })
        
        try:
            _engine = create_engine(settings.database_url, **engine_kwargs)
            # 测试连接
            with _engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("=== Database engine created successfully ===")
        except Exception as e:
            logger.error(f"=== Database connection failed: {e} ===")
            logger.error("=== Application will start without database ===")
            # 即使连接失败也返回引擎，让应用继续启动
            _engine = create_engine("sqlite:///:memory:", echo=False)
        
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
    
    return _engine

def get_db():
    """获取数据库会话"""
    engine = get_engine()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
