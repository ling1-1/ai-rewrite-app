from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

from app.core.config import settings

# 数据库连接配置
connect_args = {
    "future": True,
}

# PostgreSQL 连接池配置（Neon）
if settings.database_url.startswith("postgresql"):
    connect_args.update({
        "poolclass": QueuePool,
        "pool_size": 10,  # 连接池大小
        "max_overflow": 20,  # 最大溢出连接数
        "pool_pre_ping": True,  # 自动检测失效连接
        "pool_recycle": 1800,  # 30 分钟回收连接（防止 SSL 断开）
    })

engine = create_engine(settings.database_url, **connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

