import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import ProgrammingError

from app.api.routes import auth, history, rewrite, config, admin_manage, admin, defense
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.services.vector_db_backend import init_vector_db

print("=== Starting AI Rewrite API ===", file=sys.stderr, flush=True)

def initialize_database() -> None:
    print("=== Initializing database... ===", file=sys.stderr, flush=True)
    try:
        Base.metadata.create_all(bind=engine)
        print("=== Database initialized successfully ===", file=sys.stderr, flush=True)
    except ProgrammingError as exc:
        message = str(getattr(exc, "orig", exc)).lower()
        if "already exists" not in message and "duplicate" not in message:
            print(f"=== Database error: {exc} ===", file=sys.stderr, flush=True)
            raise
        print("=== Database tables already exist ===", file=sys.stderr, flush=True)
    except Exception as exc:
        print(f"=== Database initialization failed: {exc} ===", file=sys.stderr, flush=True)
        print("=== Continuing startup without database initialization ===", file=sys.stderr, flush=True)

initialize_database()

# 延迟初始化向量数据库（避免启动卡住）
print("=== Skipping vector DB initialization (lazy load) ===", file=sys.stderr, flush=True)
# init_vector_db()

print("=== Creating FastAPI app... ===", file=sys.stderr, flush=True)
app = FastAPI(title=settings.app_name)

print("=== Adding CORS middleware... ===", file=sys.stderr, flush=True)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "*",  # 允许所有来源（HF Space 需要）
    ],
    allow_origin_regex=r"https?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("=== Registering routers... ===", file=sys.stderr, flush=True)
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(rewrite.router, prefix="/rewrite", tags=["rewrite"])
app.include_router(defense.router, prefix="/defense", tags=["defense"])
app.include_router(history.router, prefix="/history", tags=["history"])
app.include_router(config.router, prefix="/config", tags=["config"])
app.include_router(admin.router, prefix="/admin/config", tags=["admin-config"])
app.include_router(admin_manage.router, prefix="/admin", tags=["admin-manage"])

print("=== AI Rewrite API started successfully! ===", file=sys.stderr, flush=True)

@app.get("/health")
def health_check():
    return {"status": "healthy", "app": "ai-rewrite-api"}
