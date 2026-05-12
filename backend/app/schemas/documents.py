from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class DocumentBase(BaseModel):
    file_name: str = Field(..., min_length=1, max_length=255)


class DocumentCreate(DocumentBase):
    task_id: Optional[int] = None


class DocumentOut(BaseModel):
    id: int
    file_name: str
    version: int
    uploaded_by: int
    task_id: Optional[int]
    created_at: datetime
    file_path: str

    class Config:
        from_attributes = True


class DocumentVersion(BaseModel):
    version: int
    created_at: datetime
    uploaded_by: int
    file_name: str