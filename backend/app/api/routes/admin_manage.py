"""
管理员管理 API

支持：
- 用户管理（增删改查）
- 历史记录管理（查看所有用户的历史记录）
- 数据库可视化操作
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from typing import List, Optional

from app.api.deps import get_db, get_current_admin_user
from app.models.user import User
from app.models.rewrite_record import RewriteRecord
from app.schemas.auth import RegisterRequest
from app.core.security import hash_password

router = APIRouter()


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
    
    total = db.scalar(select(func.count()).select_from(User))
    
    return {
        "users": users,
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.post("/users", summary="创建用户")
def create_user(
    payload: RegisterRequest,
    is_admin: bool = False,
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
        is_admin=is_admin
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return {"message": "用户创建成功", "user": user}


@router.put("/users/{user_id}", summary="更新用户")
def update_user(
    user_id: int,
    username: Optional[str] = None,
    password: Optional[str] = None,
    is_admin: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """管理员更新用户信息"""
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    if username:
        existing = db.scalar(select(User).where(User.username == username).where(User.id != user_id))
        if existing:
            raise HTTPException(status_code=400, detail="该用户名已存在")
        user.username = username
    
    if password:
        user.password_hash = hash_password(password)
    
    if is_admin is not None:
        user.is_admin = is_admin
    
    db.commit()
    db.refresh(user)
    
    return {"message": "用户更新成功", "user": user}


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
    
    total = db.scalar(select(func.count()).select_from(RewriteRecord))
    
    return {
        "records": records,
        "total": total,
        "limit": limit,
        "offset": offset
    }


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
