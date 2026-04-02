"""
配置管理 API
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any

from app.api.deps import get_db
from app.api.deps_admin import get_current_admin_user
from app.core.config import settings
from app.services.config_service import ConfigService
from app.models.user import User

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


class DefensePromptResponse(BaseModel):
    system_prompt: str
    ppt_prompt: str
    speech_prompt: str


class DefensePromptUpdateRequest(BaseModel):
    system_prompt: Optional[str] = None
    ppt_prompt: Optional[str] = None
    speech_prompt: Optional[str] = None


class FeatureFlagsResponse(BaseModel):
    """功能开关响应"""
    enable_registration: bool


class ModelConfigResponse(BaseModel):
    rewrite_api_key: str
    rewrite_model: str
    rewrite_base_url: str
    rewrite_max_tokens: int
    rewrite_temperature: float
    defense_api_key: str
    defense_model: str
    defense_base_url: str
    defense_max_tokens: int
    defense_temperature: float


class ModelConfigUpdateRequest(BaseModel):
    rewrite_api_key: Optional[str] = None
    rewrite_model: Optional[str] = None
    rewrite_base_url: Optional[str] = None
    rewrite_max_tokens: Optional[int] = None
    rewrite_temperature: Optional[float] = None
    defense_api_key: Optional[str] = None
    defense_model: Optional[str] = None
    defense_base_url: Optional[str] = None
    defense_max_tokens: Optional[int] = None
    defense_temperature: Optional[float] = None


@router.get("", summary="获取所有配置", tags=["admin"])
def get_all_configs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """获取所有配置（需要管理员权限）"""
    config_service = ConfigService(db)
    configs = config_service.get_all()
    return configs


@router.get("/rag/config", response_model=RAGConfigResponse, summary="获取 RAG 配置", tags=["admin"])
def get_rag_config(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """获取 RAG 检索配置（需要管理员权限）"""
    config_service = ConfigService(db)
    return config_service.get_rag_config()


@router.put("/rag/config", response_model=RAGConfigResponse, summary="更新 RAG 配置", tags=["admin"])
def update_rag_config(
    request: RAGConfigUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """更新 RAG 检索配置（需要管理员权限）"""
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


@router.get("/prompt/system", response_model=SystemPromptResponse, summary="获取系统提示词", tags=["admin"])
def get_system_prompt(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """获取系统提示词（需要管理员权限）"""
    config_service = ConfigService(db)
    return {"prompt": config_service.get_system_prompt()}


@router.put("/prompt/system", response_model=SystemPromptResponse, summary="更新系统提示词", tags=["admin"])
def update_system_prompt(
    request: SystemPromptUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """更新系统提示词（需要管理员权限）"""
    config_service = ConfigService(db)
    config_service.set('system_prompt', request.prompt)
    return {"prompt": request.prompt}


@router.get("/prompt/defense", response_model=DefensePromptResponse, summary="获取答辩辅助提示词", tags=["admin"])
def get_defense_prompt(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    config_service = ConfigService(db)
    from app.services.defense import (
        DEFENSE_SYSTEM_PROMPT,
        DEFENSE_PPT_PROMPT_TEMPLATE,
        DEFENSE_SPEECH_PROMPT_TEMPLATE,
    )

    return {
        "system_prompt": config_service.get_defense_system_prompt() or DEFENSE_SYSTEM_PROMPT,
        "ppt_prompt": config_service.get_defense_ppt_prompt() or DEFENSE_PPT_PROMPT_TEMPLATE,
        "speech_prompt": config_service.get_defense_speech_prompt() or DEFENSE_SPEECH_PROMPT_TEMPLATE,
    }


@router.put("/prompt/defense", response_model=DefensePromptResponse, summary="更新答辩辅助提示词", tags=["admin"])
def update_defense_prompt(
    request: DefensePromptUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    config_service = ConfigService(db)
    from app.services.defense import (
        DEFENSE_SYSTEM_PROMPT,
        DEFENSE_PPT_PROMPT_TEMPLATE,
        DEFENSE_SPEECH_PROMPT_TEMPLATE,
    )

    if request.system_prompt is not None:
        config_service.set("defense_system_prompt", request.system_prompt)
    if request.ppt_prompt is not None:
        config_service.set("defense_ppt_prompt", request.ppt_prompt)
    if request.speech_prompt is not None:
        config_service.set("defense_speech_prompt", request.speech_prompt)

    return {
        "system_prompt": config_service.get_defense_system_prompt() or DEFENSE_SYSTEM_PROMPT,
        "ppt_prompt": config_service.get_defense_ppt_prompt() or DEFENSE_PPT_PROMPT_TEMPLATE,
        "speech_prompt": config_service.get_defense_speech_prompt() or DEFENSE_SPEECH_PROMPT_TEMPLATE,
    }


@router.get("/flags", response_model=FeatureFlagsResponse, summary="获取功能开关", tags=["admin"])
def get_feature_flags(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """获取功能开关状态（需要管理员权限）"""
    config_service = ConfigService(db)
    return {
        "enable_registration": config_service.is_registration_enabled()
    }


@router.put("/flags/registration", response_model=FeatureFlagsResponse, summary="更新注册开关", tags=["admin"])
def update_registration_flag(
    enable: bool,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """更新注册功能开关（需要管理员权限）"""
    config_service = ConfigService(db)
    config_service.set('enable_registration', str(enable).lower())
    return {"enable_registration": enable}


@router.get("/model/config", response_model=ModelConfigResponse, summary="获取模型配置", tags=["admin"])
def get_model_config(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    config_service = ConfigService(db)
    return {
        "rewrite_api_key": config_service.get_rewrite_api_key(settings.anthropic_api_key),
        "rewrite_model": config_service.get_rewrite_model(settings.anthropic_model),
        "rewrite_base_url": config_service.get_rewrite_base_url(settings.anthropic_base_url),
        "rewrite_max_tokens": config_service.get_rewrite_max_tokens(settings.anthropic_max_tokens),
        "rewrite_temperature": config_service.get_rewrite_temperature(settings.anthropic_temperature),
        "defense_api_key": config_service.get_defense_api_key(settings.defense_api_key or settings.anthropic_api_key),
        "defense_model": config_service.get_defense_model(settings.defense_model),
        "defense_base_url": config_service.get_defense_base_url(settings.defense_base_url or settings.anthropic_base_url),
        "defense_max_tokens": config_service.get_defense_max_tokens(settings.defense_max_tokens),
        "defense_temperature": config_service.get_defense_temperature(settings.defense_temperature),
    }


@router.put("/model/config", response_model=ModelConfigResponse, summary="更新模型配置", tags=["admin"])
def update_model_config(
    request: ModelConfigUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    config_service = ConfigService(db)

    if request.rewrite_api_key is not None:
        config_service.set("rewrite_api_key", request.rewrite_api_key.strip())

    if request.rewrite_model is not None:
        config_service.set("rewrite_model", request.rewrite_model.strip())

    if request.rewrite_base_url is not None:
        config_service.set("rewrite_base_url", request.rewrite_base_url.strip())

    if request.rewrite_max_tokens is not None:
        if not (256 <= request.rewrite_max_tokens <= 16384):
            raise HTTPException(400, "rewrite_max_tokens 必须在 256-16384 之间")
        config_service.set("rewrite_max_tokens", request.rewrite_max_tokens)

    if request.rewrite_temperature is not None:
        if not (0 <= request.rewrite_temperature <= 2):
            raise HTTPException(400, "rewrite_temperature 必须在 0-2 之间")
        config_service.set("rewrite_temperature", request.rewrite_temperature)

    if request.defense_api_key is not None:
        config_service.set("defense_api_key", request.defense_api_key.strip())

    if request.defense_model is not None:
        config_service.set("defense_model", request.defense_model.strip())

    if request.defense_base_url is not None:
        config_service.set("defense_base_url", request.defense_base_url.strip())

    if request.defense_max_tokens is not None:
        if not (256 <= request.defense_max_tokens <= 8192):
            raise HTTPException(400, "defense_max_tokens 必须在 256-8192 之间")
        config_service.set("defense_max_tokens", request.defense_max_tokens)

    if request.defense_temperature is not None:
        if not (0 <= request.defense_temperature <= 2):
            raise HTTPException(400, "defense_temperature 必须在 0-2 之间")
        config_service.set("defense_temperature", request.defense_temperature)

    return {
        "rewrite_api_key": config_service.get_rewrite_api_key(settings.anthropic_api_key),
        "rewrite_model": config_service.get_rewrite_model(settings.anthropic_model),
        "rewrite_base_url": config_service.get_rewrite_base_url(settings.anthropic_base_url),
        "rewrite_max_tokens": config_service.get_rewrite_max_tokens(settings.anthropic_max_tokens),
        "rewrite_temperature": config_service.get_rewrite_temperature(settings.anthropic_temperature),
        "defense_api_key": config_service.get_defense_api_key(settings.defense_api_key or settings.anthropic_api_key),
        "defense_model": config_service.get_defense_model(settings.defense_model),
        "defense_base_url": config_service.get_defense_base_url(settings.defense_base_url or settings.anthropic_base_url),
        "defense_max_tokens": config_service.get_defense_max_tokens(settings.defense_max_tokens),
        "defense_temperature": config_service.get_defense_temperature(settings.defense_temperature),
    }


@router.get("/{key}", response_model=ConfigResponse, summary="获取单个配置")
def get_config(
    key: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """获取指定配置"""
    config_service = ConfigService(db)
    value = config_service.get(key)

    if value is None:
        raise HTTPException(status_code=404, detail=f"配置 {key} 不存在")

    return {"key": key, "value": value, "description": ""}


@router.put("/{key}", response_model=ConfigResponse, summary="更新配置")
def update_config(
    key: str,
    request: ConfigUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """更新指定配置"""
    config_service = ConfigService(db)
    config_service.set(key, request.value, request.description)

    return {"key": key, "value": request.value, "description": request.description}
