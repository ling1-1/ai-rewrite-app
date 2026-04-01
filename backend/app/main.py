from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import ProgrammingError

from app.api.routes import auth, history, rewrite, config
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine


def initialize_database() -> None:
    try:
        Base.metadata.create_all(bind=engine)
    except ProgrammingError as exc:
        message = str(getattr(exc, "orig", exc)).lower()
        if "already exists" not in message and "duplicate" not in message:
            raise


initialize_database()

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(rewrite.router, prefix="/rewrite", tags=["rewrite"])
app.include_router(history.router, prefix="/history", tags=["history"])
app.include_router(config.router, prefix="/config", tags=["config"])


@app.get("/health")
def health_check():
    return {"status": "ok"}
