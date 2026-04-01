"""
配置管理 API
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any

from app.api.deps import get_db
from app.services.config_service import ConfigService

router = APIRouter()


class ConfigResponse(BaseModel):
    """配置响应"""
    key: str
    value: Any
    description: Optional[str]


class ConfigUpdateRequest(BaseModel):
    """配置更新请求"""
    value: Any
    description: Optional[str] = None


class RAGConfigResponse(BaseModel):
    """RAG 配置响应"""
    top_k: int
    similarity_threshold: float


class RAGConfigUpdateRequest(BaseModel):
    """RAG 配置更新请求"""
    top_k: Optional[int] = None
    similarity_threshold: Optional[float] = None


class SystemPromptResponse(BaseModel):
    """系统提示词响应"""
    prompt: str


class SystemPromptUpdateRequest(BaseModel):
    """系统提示词更新请求"""
    prompt: str


class FeatureFlagsResponse(BaseModel):
    """功能开关响应"""
    enable_registration: bool


@router.get("", summary="获取所有配置")
def get_all_configs(db: Session = Depends(get_db)):
    """获取所有配置"""
    config_service = ConfigService(db)
    configs = config_service.get_all()
    return configs


@router.get("/{key}", response_model=ConfigResponse, summary="获取单个配置")
def get_config(key: str, db: Session = Depends(get_db)):
    """获取指定配置"""
    config_service = ConfigService(db)
    value = config_service.get(key)
    
    if value is None:
        raise HTTPException(status_code=404, detail=f"配置 {key} 不存在")
    
    return {"key": key, "value": value, "description": ""}


@router.put("/{key}", response_model=ConfigResponse, summary="更新配置")
def update_config(key: str, request: ConfigUpdateRequest, db: Session = Depends(get_db)):
    """更新指定配置"""
    config_service = ConfigService(db)
    config_service.set(key, request.value, request.description)
    
    return {"key": key, "value": request.value, "description": request.description}


@router.get("/rag/config", response_model=RAGConfigResponse, summary="获取 RAG 配置")
def get_rag_config(db: Session = Depends(get_db)):
    """获取 RAG 检索配置"""
    config_service = ConfigService(db)
    return config_service.get_rag_config()


@router.put("/rag/config", response_model=RAGConfigResponse, summary="更新 RAG 配置")
def update_rag_config(request: RAGConfigUpdateRequest, db: Session = Depends(get_db)):
    """更新 RAG 检索配置"""
    config_service = ConfigService(db)
    
    if request.top_k is not None:
        if not (1 <= request.top_k <= 10):
            raise HTTPException(400, "top_k 必须在 1-10 之间")
        config_service.set('rag_top_k', request.top_k)
    
    if request.similarity_threshold is not None:
        if not (0 <= request.similarity_threshold <= 1):
            raise HTTPException(400, "similarity_threshold 必须在 0-1 之间")
        config_service.set('rag_similarity_threshold', request.similarity_threshold)
    
    return config_service.get_rag_config()


@router.get("/prompt/system", response_model=SystemPromptResponse, summary="获取系统提示词")
def get_system_prompt(db: Session = Depends(get_db)):
    """获取系统提示词"""
    config_service = ConfigService(db)
    return {"prompt": config_service.get_system_prompt()}


@router.put("/prompt/system", response_model=SystemPromptResponse, summary="更新系统提示词")
def update_system_prompt(request: SystemPromptUpdateRequest, db: Session = Depends(get_db)):
    """更新系统提示词"""
    config_service = ConfigService(db)
    config_service.set('system_prompt', request.prompt)
    return {"prompt": request.prompt}


@router.get("/flags", response_model=FeatureFlagsResponse, summary="获取功能开关")
def get_feature_flags(db: Session = Depends(get_db)):
    """获取功能开关状态"""
    config_service = ConfigService(db)
    return {
        "enable_registration": config_service.is_registration_enabled()
    }


@router.put("/flags/registration", response_model=FeatureFlagsResponse, summary="更新注册开关")
def update_registration_flag(enable: bool, db: Session = Depends(get_db)):
    """更新注册功能开关"""
    config_service = ConfigService(db)
    config_service.set('enable_registration', str(enable).lower())
    return {"enable_registration": enable}
