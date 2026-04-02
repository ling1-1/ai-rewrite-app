"""
配置管理 API
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.core.rag_config import get_rag_config, update_rag_config, RAGConfig
from app.services.config_service import ConfigService
from sqlalchemy.orm import Session

router = APIRouter()


class RAGConfigResponse(BaseModel):
    """RAG 配置响应"""
    top_k: int
    similarity_threshold: float
    enabled: bool


class RAGConfigUpdateRequest(BaseModel):
    """RAG 配置更新请求"""
    top_k: Optional[int] = None
    similarity_threshold: Optional[float] = None
    enabled: Optional[bool] = None


class PublicFlagsResponse(BaseModel):
    enable_registration: bool


@router.get("/public/flags", response_model=PublicFlagsResponse)
def get_public_flags(db: Session = Depends(get_db)):
    config_service = ConfigService(db)
    return {"enable_registration": config_service.is_registration_enabled()}


@router.get("/rag", response_model=RAGConfigResponse)
def get_rag_config_api(current_user: User = Depends(get_current_user)):
    """获取 RAG 配置"""
    config = get_rag_config()
    return {
        "top_k": config.top_k,
        "similarity_threshold": config.similarity_threshold,
        "enabled": config.enabled
    }


@router.put("/rag", response_model=RAGConfigResponse)
def update_rag_config_api(
    request: RAGConfigUpdateRequest,
    current_user: User = Depends(get_current_user)
):
    """更新 RAG 配置"""
    try:
        config = update_rag_config(
            top_k=request.top_k,
            similarity_threshold=request.similarity_threshold,
            enabled=request.enabled
        )
        return {
            "top_k": config.top_k,
            "similarity_threshold": config.similarity_threshold,
            "enabled": config.enabled
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
