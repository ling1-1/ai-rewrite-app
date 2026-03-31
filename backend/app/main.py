from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, history, rewrite
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(rewrite.router, prefix="/api/rewrite", tags=["rewrite"])
app.include_router(history.router, prefix="/api/history", tags=["history"])


@app.get("/health")
def health_check():
    return {"status": "ok"}

