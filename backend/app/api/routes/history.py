"""
历史记录 API

支持：查看、重命名、收藏、删除、批量操作
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.rewrite_record import RewriteRecord
from app.models.user import User
from app.schemas.history import HistoryItemResponse, HistoryRecordUpdate, HistoryBatchDeleteRequest

router = APIRouter()


@router.get("", response_model=List[HistoryItemResponse], summary="获取历史记录")
def list_history(
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    is_favorite: Optional[bool] = Query(None, description="筛选收藏记录"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户历史记录（支持筛选、搜索、分页）"""
    query = select(RewriteRecord).where(RewriteRecord.user_id == current_user.id)
    
    # 筛选收藏
    if is_favorite is not None:
        query = query.where(RewriteRecord.is_favorite == is_favorite)
    
    # 搜索
    if search:
        query = query.where(
            (RewriteRecord.name.ilike(f"%{search}%")) |
            (RewriteRecord.source_text.ilike(f"%{search}%")) |
            (RewriteRecord.result_text.ilike(f"%{search}%"))
        )
    
    # 排序（收藏优先，然后按时间）
    query = query.order_by(
        RewriteRecord.is_favorite.desc(),
        RewriteRecord.created_at.desc()
    )
    
    # 分页
    query = query.offset(offset).limit(limit)
    
    return list(db.scalars(query).all())


@router.get("/{record_id}", response_model=HistoryItemResponse, summary="获取单条记录")
def get_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取指定历史记录"""
    record = db.get(RewriteRecord, record_id)
    
    if not record or record.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="记录不存在")
    
    return record


@router.put("/{record_id}", response_model=HistoryItemResponse, summary="更新记录（重命名、备注）")
def update_record(
    record_id: int,
    request: HistoryRecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新历史记录（重命名、添加备注）"""
    record = db.get(RewriteRecord, record_id)
    
    if not record or record.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="记录不存在")
    
    # 更新字段
    if request.name is not None:
        record.name = request.name
    if request.notes is not None:
        record.notes = request.notes
    
    db.commit()
    db.refresh(record)
    
    return record


@router.put("/{record_id}/favorite", response_model=HistoryItemResponse, summary="收藏/取消收藏")
def toggle_favorite(
    record_id: int,
    is_favorite: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """收藏或取消收藏历史记录"""
    record = db.get(RewriteRecord, record_id)
    
    if not record or record.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="记录不存在")
    
    record.is_favorite = is_favorite
    db.commit()
    db.refresh(record)
    
    return record


@router.delete("/{record_id}", summary="删除记录")
def delete_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除历史记录"""
    record = db.get(RewriteRecord, record_id)
    
    if not record or record.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="记录不存在")
    
    db.delete(record)
    db.commit()
    
    return {"message": "删除成功", "record_id": record_id}


@router.post("/batch-delete", summary="批量删除")
def batch_delete_records(
    request: HistoryBatchDeleteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """批量删除历史记录"""
    # 验证记录属于当前用户
    records = db.scalars(
        select(RewriteRecord).where(
            RewriteRecord.id.in_(request.ids),
            RewriteRecord.user_id == current_user.id
        )
    ).all()
    
    if len(records) != len(request.ids):
        raise HTTPException(status_code=404, detail="部分记录不存在或无权删除")
    
    # 批量删除
    for record in records:
        db.delete(record)
    
    db.commit()
    
    return {
        "message": f"成功删除 {len(records)} 条记录",
        "deleted_count": len(records)
    }

