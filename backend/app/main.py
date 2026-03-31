from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import ProgrammingError

from app.api.routes import auth, history, rewrite
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine


BASE_DIR = Path(__file__).resolve().parents[2]
PUBLIC_DIR = BASE_DIR / "public"


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

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(rewrite.router, prefix="/api/rewrite", tags=["rewrite"])
app.include_router(history.router, prefix="/api/history", tags=["history"])

if (PUBLIC_DIR / "assets").exists():
    app.mount("/assets", StaticFiles(directory=PUBLIC_DIR / "assets"), name="assets")


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/", include_in_schema=False)
def serve_homepage():
    return _serve_public_file("index.html")


@app.get("/{full_path:path}", include_in_schema=False)
def serve_spa(full_path: str):
    if full_path.startswith(("api/", "health")):
        raise HTTPException(status_code=404, detail="Not Found")

    return _serve_public_file(full_path or "index.html", fallback_to_index=True)


def _serve_public_file(path: str, fallback_to_index: bool = False) -> FileResponse:
    candidate = (PUBLIC_DIR / path).resolve()
    public_root = PUBLIC_DIR.resolve()

    if candidate.is_file() and str(candidate).startswith(str(public_root)):
        return FileResponse(candidate)

    if fallback_to_index and (PUBLIC_DIR / "index.html").is_file():
        return FileResponse(PUBLIC_DIR / "index.html")

    raise HTTPException(status_code=404, detail="Not Found")
