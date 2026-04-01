from datetime import datetime

from pydantic import BaseModel


class HistoryItemResponse(BaseModel):
    id: int
    source_text: str
    result_text: str
    created_at: datetime

    class Config:
        from_attributes = True

