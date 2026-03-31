from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.rewrite_record import RewriteRecord
from app.models.user import User
from app.schemas.rewrite import FileExtractResponse, RewriteRequest, RewriteResponse
from app.services.file_extract import FileExtractError, extract_text_from_upload
from app.services.rewrite import RewriteServiceError, rewrite_text

router = APIRouter()


@router.post("", response_model=RewriteResponse)
def create_rewrite(
    payload: RewriteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not payload.source_text.strip():
        raise HTTPException(status_code=400, detail="原文不能为空")

    try:
        result_text = rewrite_text(payload.source_text)
    except RewriteServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    record = RewriteRecord(
        user_id=current_user.id,
        source_text=payload.source_text,
        result_text=result_text,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return record


@router.post("/extract-file", response_model=FileExtractResponse)
def extract_file_content(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    del current_user

    try:
        source_text = extract_text_from_upload(file)
    except FileExtractError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "filename": file.filename or "未命名文件",
        "source_text": source_text,
        "char_count": len(source_text),
    }
