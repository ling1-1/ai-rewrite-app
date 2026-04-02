"""
管理员管理 API

支持：
- 用户管理（增删改查）
- 历史记录管理（查看所有用户的历史记录）
- 数据库可视化操作
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from typing import List, Optional

from app.api.deps import get_db
from app.api.deps_admin import get_current_admin_user
from app.core.security import hash_password
from app.models.rewrite_record import RewriteRecord
from app.models.user import User

router = APIRouter()


class AdminUserCreateRequest(BaseModel):
    username: str
    password: str
    is_admin: bool = False


class AdminUserUpdateRequest(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    is_admin: Optional[bool] = None


class AdminHistoryUpdateRequest(BaseModel):
    name: Optional[str] = None
    source_text: Optional[str] = None
    result_text: Optional[str] = None
    notes: Optional[str] = None
    is_favorite: Optional[bool] = None


def serialize_user(user: User) -> dict:
    return {
        "id": user.id,
        "username": user.username,
        "is_admin": user.is_admin,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
    }


def serialize_history_record(record: RewriteRecord) -> dict:
    return {
        "id": record.id,
        "user_id": record.user_id,
        "username": record.user.username if record.user else None,
        "name": record.name,
        "source_text": record.source_text,
        "result_text": record.result_text,
        "notes": record.notes,
        "is_favorite": record.is_favorite,
        "created_at": record.created_at,
        "updated_at": record.updated_at,
    }


# ==================== 用户管理 ====================

@router.get("/users", summary="查看所有用户")
def list_users(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    search: Optional[str] = Query(None, description="搜索用户名"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """管理员查看所有用户（支持搜索、分页）"""
    query = select(User)
    
    if search:
        query = query.where(User.username.ilike(f"%{search}%"))
    
    query = query.order_by(User.created_at.desc()).offset(offset).limit(limit)
    users = db.scalars(query).all()

    total_query = select(func.count()).select_from(User)
    if search:
        total_query = total_query.where(User.username.ilike(f"%{search}%"))
    total = db.scalar(total_query)
    
    return {
        "users": [serialize_user(user) for user in users],
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.post("/users", summary="创建用户")
def create_user(
    payload: AdminUserCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """管理员创建用户"""
    existing_user = db.scalar(select(User).where(User.username == payload.username))
    if existing_user:
        raise HTTPException(status_code=400, detail="该用户名已注册")
    
    user = User(
        username=payload.username,
        password_hash=hash_password(payload.password),
        is_admin=payload.is_admin
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return {"message": "用户创建成功", "user": serialize_user(user)}


@router.put("/users/{user_id}", summary="更新用户")
def update_user(
    user_id: int,
    payload: AdminUserUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """管理员更新用户信息"""
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    if payload.username:
        existing = db.scalar(select(User).where(User.username == payload.username).where(User.id != user_id))
        if existing:
            raise HTTPException(status_code=400, detail="该用户名已存在")
        user.username = payload.username
    
    if payload.password:
        user.password_hash = hash_password(payload.password)
    
    if payload.is_admin is not None:
        if user.id == current_user.id and payload.is_admin is False:
            raise HTTPException(status_code=400, detail="不能取消自己的管理员权限")
        user.is_admin = payload.is_admin
    
    db.commit()
    db.refresh(user)
    
    return {"message": "用户更新成功", "user": serialize_user(user)}


@router.delete("/users/{user_id}", summary="删除用户")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """管理员删除用户"""
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="不能删除自己")
    
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    db.delete(user)
    db.commit()
    
    return {"message": "用户删除成功"}


# ==================== 历史记录管理 ====================

@router.get("/history/all", summary="查看所有历史记录")
def list_all_history(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    user_id: Optional[int] = Query(None, description="筛选特定用户"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """管理员查看所有用户的历史记录"""
    query = select(RewriteRecord)
    
    if user_id:
        query = query.where(RewriteRecord.user_id == user_id)
    
    if search:
        query = query.where(
            (RewriteRecord.name.ilike(f"%{search}%")) |
            (RewriteRecord.source_text.ilike(f"%{search}%")) |
            (RewriteRecord.result_text.ilike(f"%{search}%"))
        )
    
    query = query.order_by(RewriteRecord.created_at.desc()).offset(offset).limit(limit)
    records = db.scalars(query).all()

    total_query = select(func.count()).select_from(RewriteRecord)
    if user_id:
        total_query = total_query.where(RewriteRecord.user_id == user_id)
    if search:
        total_query = total_query.where(
            (RewriteRecord.name.ilike(f"%{search}%")) |
            (RewriteRecord.source_text.ilike(f"%{search}%")) |
            (RewriteRecord.result_text.ilike(f"%{search}%"))
        )
    total = db.scalar(total_query)
    
    return {
        "records": [serialize_history_record(record) for record in records],
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.get("/history/{record_id}", summary="查看单条历史记录")
def get_history_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    record = db.get(RewriteRecord, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")

    return serialize_history_record(record)


@router.put("/history/{record_id}", summary="更新历史记录")
def update_history_record(
    record_id: int,
    payload: AdminHistoryUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    record = db.get(RewriteRecord, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")

    if payload.name is not None:
        record.name = payload.name
    if payload.source_text is not None:
        record.source_text = payload.source_text
    if payload.result_text is not None:
        record.result_text = payload.result_text
    if payload.notes is not None:
        record.notes = payload.notes
    if payload.is_favorite is not None:
        record.is_favorite = payload.is_favorite

    db.commit()
    db.refresh(record)

    return {"message": "记录更新成功", "record": serialize_history_record(record)}


@router.delete("/history/{record_id}", summary="删除历史记录")
def delete_history_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """管理员删除任意历史记录"""
    record = db.get(RewriteRecord, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    
    db.delete(record)
    db.commit()
    
    return {"message": "记录删除成功"}


@router.post("/history/batch-delete", summary="批量删除历史记录")
def batch_delete_history(
    record_ids: List[int],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """管理员批量删除历史记录"""
    records = db.scalars(select(RewriteRecord).where(RewriteRecord.id.in_(record_ids))).all()
    
    for record in records:
        db.delete(record)
    
    db.commit()
    
    return {
        "message": f"成功删除 {len(records)} 条记录",
        "deleted_count": len(records)
    }
