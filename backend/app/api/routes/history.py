from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.rewrite_record import RewriteRecord
from app.models.user import User
from app.schemas.history import HistoryItemResponse

router = APIRouter()


@router.get("", response_model=List[HistoryItemResponse])
def list_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = (
        select(RewriteRecord)
        .where(RewriteRecord.user_id == current_user.id)
        .order_by(desc(RewriteRecord.created_at))
    )
    return list(db.scalars(query).all())

