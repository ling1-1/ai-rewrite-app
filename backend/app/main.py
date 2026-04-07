import sys
import os

# 强制刷新日志输出
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

print("=== Application Startup ===", flush=True)
print(f"=== Python Version: {sys.version} ===", flush=True)
print(f"=== Working Dir: {os.getcwd()} ===", flush=True)
print(f"=== PYTHONUNBUFFERED: {os.environ.get('PYTHONUNBUFFERED', 'NOT SET')} ===", flush=True)

try:
    import logging
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    
    print("=== FastAPI imported successfully ===", flush=True)
    
    from app.api.routes import auth, history, rewrite, config, admin_manage, admin, defense
    print("=== Routes imported successfully ===", flush=True)
    
    from app.core.config import settings
    print(f"=== Settings loaded: {settings.app_name} ===", flush=True)
    
    from app.db.session import get_engine
    print("=== DB session imported (lazy load) ===", flush=True)
    
    # 检查环境变量
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        print(f"=== DATABASE_URL: {database_url[:50]}... ===", flush=True)
    else:
        print("=== DATABASE_URL: NOT CONFIGURED ===", flush=True)
    
    secret_key = os.environ.get("SECRET_KEY")
    if secret_key:
        print(f"=== SECRET_KEY: configured ===", flush=True)
    else:
        print("=== SECRET_KEY: NOT CONFIGURED ===", flush=True)
    
    print("=== Creating FastAPI app ===", flush=True)
    app = FastAPI(title=settings.app_name)
    print("=== FastAPI app created ===", flush=True)
    
    print("=== Adding CORS middleware ===", flush=True)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_origin_regex=r"https?://.*",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    print("=== CORS middleware added ===", flush=True)
    
    print("=== Registering routers ===", flush=True)
    app.include_router(auth.router, prefix="/auth", tags=["auth"])
    app.include_router(rewrite.router, prefix="/rewrite", tags=["rewrite"])
    app.include_router(defense.router, prefix="/defense", tags=["defense"])
    app.include_router(history.router, prefix="/history", tags=["history"])
    app.include_router(config.router, prefix="/config", tags=["config"])
    app.include_router(admin.router, prefix="/admin/config", tags=["admin-config"])
    app.include_router(admin_manage.router, prefix="/admin", tags=["admin-manage"])
    print("=== Routers registered ===", flush=True)
    
    @app.get("/health")
    def health_check():
        return {
            "status": "healthy",
            "app": settings.app_name,
            "version": "2026.04.07"
        }
    
    @app.get("/db/status")
    def db_status():
        try:
            engine = get_engine()
            return {"status": "connected", "database": "postgresql"}
        except Exception as e:
            return {"status": "disconnected", "error": str(e)}
    
    print("=== AI Rewrite API started successfully ===", flush=True)
    print("=== Health check: /health ===", flush=True)
    print("=== DB status check: /db/status ===", flush=True)
    
except Exception as e:
    print(f"=== FATAL ERROR during startup: {e} ===", flush=True)
    print(f"=== Error type: {type(e).__name__} ===", flush=True)
    import traceback
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)
