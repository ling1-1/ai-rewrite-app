from datetime import datetime

from pydantic import BaseModel


class RewriteRequest(BaseModel):
    source_text: str


class RewriteResponse(BaseModel):
    id: int
    source_text: str
    result_text: str
    created_at: datetime

    class Config:
        from_attributes = True


class FileExtractResponse(BaseModel):
    filename: str
    source_text: str
    char_count: int
