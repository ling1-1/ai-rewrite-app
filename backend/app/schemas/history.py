"""
历史记录 Schema
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class HistoryItemResponse(BaseModel):
    """历史记录响应"""
    id: int
    user_id: int
    name: Optional[str] = None
    source_text: str
    result_text: str
    is_favorite: bool = False
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class HistoryRecordUpdate(BaseModel):
    """历史记录更新请求"""
    name: Optional[str] = None
    notes: Optional[str] = None
    is_favorite: Optional[bool] = None


class HistoryBatchDeleteRequest(BaseModel):
    """批量删除请求"""
    ids: List[int]
