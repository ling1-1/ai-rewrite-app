from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.rewrite_record import RewriteRecord
from app.models.user import User
from app.schemas.rewrite import RewriteRequest, RewriteResponse
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
