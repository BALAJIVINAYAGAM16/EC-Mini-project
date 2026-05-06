from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class CommentCreate(BaseModel):
    content: str = Field(..., min_length=1)
    is_internal: Optional[bool] = False


class CommentOut(BaseModel):
    id: int
    task_id: int
    user_id: int
    content: str
    is_internal: bool
    created_at: datetime

    class Config:
        from_attributes = True